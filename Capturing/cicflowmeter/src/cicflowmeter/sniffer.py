import argparse

from scapy.sendrecv import AsyncSniffer

from .flow_session import generate_session_class

import os, glob


def create_sniffer(
    input_file, input_interface, output_mode, output_file, url_model=None, tmp_file=False #modified
):
    assert (input_file is None) ^ (input_interface is None)

    NewFlowSession = generate_session_class(output_mode, output_file, url_model, tmp_file, input_interface)

    if input_file is not None:
        return AsyncSniffer(
            offline=input_file,
            filter="ip and (tcp or udp)",
            prn=None,
            session=NewFlowSession,
            store=False,
        )
    else:
        return AsyncSniffer(
            iface=input_interface,
            filter="ip and (tcp or udp)",
            prn=None,
            session=NewFlowSession,
            store=False,
        )

def delete_temp_files(output) -> None:
    files = glob.glob(os.path.join(output, '*'))
    for file in files:
        os.remove(file)

def main():
    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i",
        "--interface",
        action="store",
        dest="input_interface",
        help="capture online data from INPUT_INTERFACE",
    )

    input_group.add_argument(
        "-f",
        "--file",
        action="store",
        dest="input_file",
        help="capture offline data from INPUT_FILE",
    )

    output_group = parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument(
        "-c",
        "--csv",
        "--flow",
        action="store_const",
        const="flow",
        dest="output_mode",
        help="output flows as csv",
    )

    url_model = parser.add_mutually_exclusive_group(required=False)
    url_model.add_argument(
        "-u",
        "--url",
        action="store",
        dest="url_model",
        help="URL endpoint for send to Machine Learning Model. e.g http://0.0.0.0:80/prediction",
    )

    # modified
    tmpfile = parser.add_mutually_exclusive_group(required=False)
    tmpfile.add_argument(
        "-t",
        "--tmp",
        action="store_const",
        const=True,
        dest="tmp_file",
        help="flows as temporary file in temporary directory",
    )

    parser.add_argument(
        "output",
        help="output file name (in flow mode) or directory (in sequence mode)",
    )

    args = parser.parse_args()

    sniffer = create_sniffer(
        args.input_file,
        args.input_interface,
        args.output_mode,
        args.output,
        args.url_model,
        # modified
        args.tmp_file
    )
    if args.tmp_file:
        delete_temp_files(args.output)
        
    sniffer.start()

    try:
        sniffer.join()
    except KeyboardInterrupt:
        sniffer.stop()
    finally:
        sniffer.join()


if __name__ == "__main__":
    main()
