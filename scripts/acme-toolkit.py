#!/usr/bin/env python


from os import get_terminal_size


deps = {"acme": "2.11.0", "cryptography": "43.0.1", "requests": "2.32.3"}

try:
    import json
    import argparse
    import os
    import sys
    import textwrap
    import josepy
    import acme.client
    import acme.errors
    import acme.messages
    import requests
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError as exc:
    print(exc)
    print(
        "\nYou're missing required packages. Try running the following command in a virtual environment:"
    )
    print(
        "  pip install "
        + " ".join([f'"{key}=={value}"' for key, value in deps.items()])
    )
    print(
        "To create a virtual environment, you can run:\n  python3 -m venv .venv\nand then activate it with \n  source .venv/bin/activate"
    )
    sys.exit(1)

SCRIPT = os.path.basename(sys.argv[0])


def log(msg):
    print(msg, file=sys.stderr)


def bind_account():
    """allows you to perform EAB without using a client"""
    parser = argparse.ArgumentParser(f"{SCRIPT} bind-account")
    parser.add_argument(
        "-s",
        "--server",
        help="Path to the ACME directory.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--contact",
        help="Email address contact, unused but you still have to pass it!",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-i",
        "--eab-kid",
        help="External account binding key id.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-k",
        "--eab-hmac-key",
        help="External account binding hmac key.",
        type=str,
        required=True,
    )
    args = parser.parse_args(sys.argv[2:])

    try:
        directory = requests.get(args.server).json()
    except Exception as exc:
        log("Error getting directory:\n" + str(exc))
        return 1

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    account_key = josepy.JWKRSA.load(pem_private_key)

    net = acme.client.ClientNetwork(account_key, user_agent="acme-toolkit/v1")
    acme_client = acme.client.ClientV2(
        acme.client.messages.Directory.from_json(directory), net=net
    )

    eab = acme.client.messages.ExternalAccountBinding.from_data(
        account_public_key=acme_client.net.key.public_key(),
        kid=args.eab_kid,
        hmac_key=args.eab_hmac_key,
        directory=acme_client.directory,
    )

    registration = acme.client.messages.NewRegistration.from_data(
        email=args.contact,
        terms_of_service_agreed=True,
        external_account_binding=eab,
    )

    try:
        acme_client.new_account(registration)
        log("Account created successfully.\n ")
        print(pem_private_key.decode())

        return 0
    except acme.messages.Error as exc:
        log(f"{exc.typ}: {exc.description} :: {exc.detail}")

        return 1
    except acme.errors.ConflictError:
        log("Account already exists, exiting")

        return 1


def lookup_account():
    """shows account ID from jwk (using private key for input)"""
    parser = argparse.ArgumentParser(f"{SCRIPT} bind-account")
    parser.add_argument(
        "-s",
        "--server",
        help="Path to the ACME directory.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Path to the PEM-formatted private key.",
        type=str,
        required=True,
    )

    args = parser.parse_args(sys.argv[2:])
    file = open(args.input, "r")
    account_key = josepy.JWKRSA.load(file.read().encode())

    try:
        directory = requests.get(args.server).json()
    except Exception as exc:
        log("Error getting directory:\n" + str(exc))
        return 1

    net = acme.client.ClientNetwork(account_key, user_agent="acme-toolkit/v1")
    acme_client = acme.client.ClientV2(
        acme.client.messages.Directory.from_json(directory), net=net
    )

    registration = acme.client.messages.NewRegistration.from_data(
        terms_of_service_agreed=True, only_return_existing=True
    )

    try:
        acme_client.new_account(registration)
        # The new_account method should raise a ConflictError if
        # an account is found.
        raise Exception()
    except acme.errors.ConflictError as exc:
        kid = exc.location.split("/")[-1]
        log("Account found successfully")
        print(kid)
    except Exception as exc:
        log(exc)
        return 1


def pem_to_jwk():
    """converts a pem formatted key to a jwk"""
    parser = argparse.ArgumentParser(f"{SCRIPT} bind-account")
    parser.add_argument(
        "-i",
        "--input",
        help="Path to the PEM-formatted private key.",
        type=str,
        required=True,
    )
    args = parser.parse_args(sys.argv[2:])
    file = open(args.input, "r")
    jwk = josepy.JWKRSA.load(file.read().encode())
    print(json.dumps(jwk.to_json(), indent=2))


def jwk_to_pem():
    """converts a jwk formatted key to a pem"""
    parser = argparse.ArgumentParser(f"{SCRIPT} bind-account")
    parser.add_argument(
        "-i",
        "--input",
        help="Path to the jwk-formatted private key.",
        type=str,
        required=True,
    )
    args = parser.parse_args(sys.argv[2:])
    file = open(args.input, "r")
    jwk = josepy.JWKRSA.json_loads(file.read())
    as_pem = jwk.key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    print(as_pem.decode())


def show_help():
    """shows this help!"""
    usage()


def print_command_help():
    cols = get_terminal_size().columns
    command_help = [(c, func.__doc__) for c, func in commands.items()]

    help_indent = 21

    for entry in command_help:
        command, help = entry
        help_lines = textwrap.wrap(help, cols - help_indent)

        print("  {: <21} {: <20}".format(command, help_lines[0]))
        for line in help_lines[1:]:
            print("  {: <20} {: <20}".format("", line))


def usage():
    print(
        textwrap.dedent(f"""\
        {SCRIPT} is a swiss-army toolkit for ACME.
        usage: {SCRIPT} command [arguments]

        commands:""")
    )
    print_command_help()


def main() -> int:
    params = sys.argv[1:]
    if not params:
        return usage()

    command = commands.get(params[0].lower().strip(), usage)
    return command()


commands = {
    "help": show_help,
    "bind-account": bind_account,
    "lookup-account": lookup_account,
    "pem-to-jwk": pem_to_jwk,
    "jwk-to-pem": jwk_to_pem,
}

if __name__ == "__main__":
    sys.exit(main())
