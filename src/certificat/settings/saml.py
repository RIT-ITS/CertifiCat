from os import path
from .dynamic import ApplicationSettings, SAMLSettings
import inject
import saml2
import saml2.saml

dynamic_settings = inject.instance(ApplicationSettings)

BASEDIR = path.dirname(path.abspath(__file__))

if dynamic_settings.login_method == "saml":
    saml_settings = SAMLSettings.get()
    LOGIN_URL = "/saml2/login/"
    AUTHENTICATION_BACKENDS = ["certificat.auth.Saml2Backend"]

    SAML_SESSION_COOKIE_NAME = saml_settings.session_cookie

    SAML_ATTRIBUTE_MAPPING = saml_settings.attribute_mapping

    if saml_settings.discovery:
        SAML2_DISCO_URL = saml_settings.discovery.service

    SAML_ACS_FAILURE_RESPONSE_FUNCTION = "certificat.modules.html.views.acs_failure"

    SAML_CONFIG = {
        # full path to the xmlsec1 binary programm
        "xmlsec_binary": saml_settings.xmlsec_binary,
        # your entity id, usually your subdomain plus the url to the metadata view
        "entityid": saml_settings.sp.entity_id,
        # directory with attribute mapping
        "attribute_map_dir": path.join(path.dirname(BASEDIR), "saml/attribute_maps"),
        # Permits to have attributes not configured in attribute-mappings
        # otherwise...without OID will be rejected
        "allow_unknown_attributes": True,
        # this block states what services we provide
        "service": {
            # we are just a lonely SP
            "sp": {
                "name": saml_settings.sp.name,
                "name_id_format": saml2.saml.NAMEID_FORMAT_TRANSIENT,
                "endpoints": {
                    # url and binding to the assetion consumer service view
                    # do not change the binding or service name
                    "assertion_consumer_service": [
                        (
                            f"{dynamic_settings.url_root}/saml2/acs/",
                            saml2.BINDING_HTTP_POST,
                        ),
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    "single_logout_service": [
                        # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                        (
                            f"{dynamic_settings.url_root}/saml2/ls/",
                            saml2.BINDING_HTTP_REDIRECT,
                        ),
                        (
                            f"{dynamic_settings.url_root}/saml2/ls/post",
                            saml2.BINDING_HTTP_POST,
                        ),
                    ],
                },
                "signing_algorithm": saml_settings.sp.signing_algorthm,
                "digest_algorithm": saml_settings.sp.digest_algorithm,
                # Mandates that the identity provider MUST authenticate the
                # presenter directly rather than rely on a previous security context.
                "force_authn": saml_settings.sp.force_authn,
                # Enable AllowCreate in NameIDPolicy.
                "name_id_format_allow_create": False,
                # attributes that this project need to identify a user
                "required_attributes": [],
                # attributes that may be useful to have but not required
                "optional_attributes": [],
                "want_response_signed": True,
                "authn_requests_signed": False,
                "logout_requests_signed": True,
                "want_assertions_signed": False,
                "only_use_keys_in_metadata": True,
                "allow_unsolicited": saml_settings.sp.allow_unsolicited,
            },
        },
        # where the remote metadata is stored, local, remote or mdq server.
        "metadata": {
            "local": saml_settings.idp.local,
            "remote": [o.model_dump() for o in saml_settings.idp.remote],
            "mdq": [o.model_dump() for o in saml_settings.idp.mdq],
        },
        # set to 1 to output debugging information
        "debug": 1 if saml_settings.debug else 0,
        # Signing
        "key_file": saml_settings.sp.key_file,  # private part
        "cert_file": saml_settings.sp.cert_file,  # public part
        # Encryption
        "encryption_keypairs": [
            {
                "key_file": saml_settings.sp.key_file,  # private part
                "cert_file": saml_settings.sp.cert_file,  # public part
            }
        ],
        "discovery_response": saml_settings.discovery.response
        if saml_settings.discovery
        else None,
        # own metadata settings
        "contact_person": [],
        # you can set multilanguage information here
        "organization": {
            "name": [("Rochester Institute of Technology", "en")],
            "display_name": [("RIT", "en")],
            "url": [("https://rit.edu/", "en")],
        },
    }
