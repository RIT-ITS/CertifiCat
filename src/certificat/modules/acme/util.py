import logging
import secrets
import string

import dns.resolver

logger = logging.getLogger(__name__)


def gen_id(length=10) -> str:
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


class DNSTXTValidator:
    resolvers: list[dns.resolver.Resolver]
    domain: str
    token: str
    validated = False

    def __init__(self, resolvers: list[dns.resolver.Resolver], domain: str, token: str):
        self.resolvers = resolvers
        self.domain = domain
        self.token = token

    async def validate(self):
        if self.validated:
            return

        for idx, resolver in enumerate(self.resolvers):
            answers = resolver.resolve(self.domain, "TXT")
            answer_data = [answer.to_text().strip('"') for answer in answers]

            if self.token not in answer_data:
                logger.debug(f"Validation token not found for {self.domain}")
                return

            logger.debug(
                f"{self.domain} validated successfully for ns {idx + 1}/{len(self.resolvers)}"
            )

        logger.debug(f"{self.domain} validated successfully")
        self.validated = True
