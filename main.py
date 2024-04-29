import argparse
import btnWhisper
from btnWhisper import BtnWhisper
import sounddevice as sd
from openai import OpenAI
from dotenv import load_dotenv
import os


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l",
    "--list-devices",
    action="store_true",
    help="show list of audio devices and exit",
)
args, remaining = parser.parse_known_args()
if args.list_devices:
    # Return information about available devices.
    print(sd.query_devices())
    parser.exit(0)

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser],
)
parser.add_argument(
    "-d", "--device", type=int_or_str, help="input device (numeric ID or substring)"
)
parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-c", "--channels", type=int, default=1, help="number of input channels"
)
parser.add_argument(
    "-t", "--subtype", type=str, help='sound file subtype (e.g. "PCM_24")'
)
args = parser.parse_args(remaining)


try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    print("Initializing...")
    load_dotenv()
    client = OpenAI()
    btnWhisper = BtnWhisper(args, client)
    btnWhisper.add_listener()
    print("Start")
    while True:
        pass

except KeyboardInterrupt:
    print("\nEnd")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
