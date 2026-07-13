from __future__ import annotations as _annotations

from dataclasses import dataclass
import logging
from datetime import datetime, timezone
from pathlib import Path
from textwrap import wrap
from typing import Any, List

from dnslib import QTYPE, RR, DNSLabel, dns
from dnslib.proxy import ProxyResolver as LibProxyResolver
from dnslib.server import BaseResolver as LibBaseResolver, DNSServer as LibDNSServer

from .load_records import Records, Zone, load_records

__all__ = "DNSServer", "logger"

SERIAL_NO = int(
    (
        datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    ).total_seconds()
)


handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s", datefmt="%H:%M:%S"))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

TYPE_LOOKUP = {
    "A": (dns.A, QTYPE.A),
    "AAAA": (dns.AAAA, QTYPE.AAAA),
    "CAA": (dns.CAA, QTYPE.CAA),
    "CNAME": (dns.CNAME, QTYPE.CNAME),
    "DNSKEY": (dns.DNSKEY, QTYPE.DNSKEY),
    "MX": (dns.MX, QTYPE.MX),
    "NAPTR": (dns.NAPTR, QTYPE.NAPTR),
    "NS": (dns.NS, QTYPE.NS),
    "PTR": (dns.PTR, QTYPE.PTR),
    "RRSIG": (dns.RRSIG, QTYPE.RRSIG),
    "SOA": (dns.SOA, QTYPE.SOA),
    "SRV": (dns.SRV, QTYPE.SRV),
    "TXT": (dns.TXT, QTYPE.TXT),
    "SPF": (dns.TXT, QTYPE.TXT),
}
DEFAULT_PORT = 53
DEFAULT_UPSTREAM = "1.1.1.1"


class Record:
    def __init__(self, zone: Zone):
        if zone.host.startswith("*."):
            self.is_wildcard = True
            self._rname = DNSLabel(zone.host[2:])
        else:
            self.is_wildcard = False
            self._rname = DNSLabel(zone.host)
        self.zone = zone

        rd_cls, self._rtype = TYPE_LOOKUP[zone.type]

        args: list[Any]
        if isinstance(zone.answer, str):
            if self._rtype == QTYPE.TXT:
                args = [wrap(zone.answer, 255)]
            else:
                args = [zone.answer]
        else:
            if self._rtype == QTYPE.SOA and len(zone.answer) == 2:
                # add sensible times to SOA
                args = zone.answer + [(SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600)]
            else:
                args = zone.answer

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        self.rr = RR(
            rname=self._rname,
            rtype=self._rtype,
            rdata=rd_cls(*args),
            ttl=ttl,
        )

    def match(self, qtype, qname):
        if self.is_wildcard:
            return qname.matchSuffix(self._rname) and (
                qtype == QTYPE.ANY or self._rtype == QTYPE.CNAME or qtype == self._rtype
            )
        else:
            return qname == self._rname and (
                qtype == QTYPE.ANY or self._rtype == QTYPE.CNAME or qtype == self._rtype
            )

    def sub_match(self, q):
        return self._rtype == QTYPE.SOA and q.qname.matchSuffix(self._rname)

    def __str__(self):
        return str(self.rr)


@dataclass
class Query:
    qtype: str
    qname: str


def resolve(request, handler, records):
    records = [Record(zone) for zone in records.zones]
    type_name = QTYPE[request.q.qtype]
    reply = request.reply()
    logger.info("Searching with query %s", request.q)

    query = Query(request.q.qtype, request.q.qname)
    done = False
    while not done:
        reply_len = len(reply.rr)
        for record in records:
            if record.match(query.qtype, query.qname):
                reply.add_answer(record.rr)
                if record._rtype == QTYPE.CNAME:
                    query = Query(request.q.qtype, str(record.rr.rdata).rstrip("."))
                else:
                    done = True

        if reply_len == len(reply.rr):
            break

    # for record in records:
    #     if record.match(request.q):
    #         if record.is_wildcard:
    #             new_host = ".".join([x.decode() for x in request.q.qname.label])
    #             temp_zone = record.zone.clone_with_new_host(new_host)
    #             temp_record = Record(temp_zone)
    #             if temp_record.match(request.q):
    #                 reply.add_answer(temp_record.rr)
    #         else:
    #             reply.add_answer(record.rr)

    if reply.rr:
        logger.info(
            "found zone for %s[%s], %d replies",
            request.q.qname,
            type_name,
            len(reply.rr),
        )
        return reply

    # no direct zone so look for an SOA record for a higher level zone
    for record in records:
        if record.sub_match(request.q):
            reply.add_answer(record.rr)

    if reply.rr:
        logger.info(
            "found higher level SOA resource for %s[%s]", request.q.qname, type_name
        )
        return reply


class BaseResolver(LibBaseResolver):
    def __init__(self, records: Records):
        self.records = records
        super().__init__()

    def resolve(self, request, handler):
        answer = resolve(request, handler, self.records)
        if answer:
            return answer

        type_name = QTYPE[request.q.qtype]
        logger.info(
            "no local zone found, not proxying %s[%s]", request.q.qname, type_name
        )
        return request.reply()


class DNSServer:
    def __init__(
        self,
        records: Records | None = None,
        port: int | str | None = DEFAULT_PORT,
    ):
        self.port: int = DEFAULT_PORT if port is None else int(port)
        self.udp_server: LibDNSServer | None = None
        self.tcp_server: LibDNSServer | None = None
        self.records: Records = records if records else Records(zones=[])

    def start(self):
        logger.info(
            "starting DNS server on port %d, without upstream DNS server", self.port
        )
        resolver = BaseResolver(self.records)

        self.udp_server = LibDNSServer(resolver, port=self.port)
        self.tcp_server = LibDNSServer(resolver, port=self.port, tcp=True)
        self.udp_server.start_thread()
        self.tcp_server.start_thread()

    def stop(self):
        self.udp_server.stop()
        self.udp_server.server.server_close()
        self.tcp_server.stop()
        self.tcp_server.server.server_close()

    @property
    def is_running(self):
        return (self.udp_server and self.udp_server.isAlive()) or (
            self.tcp_server and self.tcp_server.isAlive()
        )

    def add_record(self, zone: Zone):
        self.records.zones.append(zone)

    def set_records(self, zones: List[Zone]):
        self.records.zones = zones
