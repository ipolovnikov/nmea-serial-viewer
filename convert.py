import os
import pynmea2

file_names = [
    "20220111T132616198_777_1.log",
    "20220111T132754720_689_1.log",
    "20220111T134830402_689_2.log",
    "20220111T134910151_777_2.log",
]

for file_name in file_names:
    with open(file_name, mode="r") as in_file, open(
        os.path.join("export", file_name + ".txt"), mode="w"
    ) as out_file:

        for line in in_file:
            try:
                if len(line) > 24:
                    msg = pynmea2.parse(line[24:])

                    if hasattr(msg, "lat"):
                        msg.lat = msg.latitude

                    if hasattr(msg, "lon"):
                        msg.lon = msg.longitude

                    output = [
                        line[:10],
                        line[11:19],
                        msg.talker,
                        msg.sentence_type,
                    ] + msg.data

                    print(output)
                    out_file.write(str.join(";", output) + "\n")
            except pynmea2.ParseError as e:
                print("Parse error: {}".format(e))
                continue
