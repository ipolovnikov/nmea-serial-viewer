import os

file_names = [
    "20220111T132616198_777_1.log.txt",
    "20220111T132754720_689_1.log.txt",
    "20220111T134830402_689_2.log.txt",
    "20220111T134910151_777_2.log.txt",
]

for file_name in file_names:
    with open(os.path.join('export', file_name), mode="r") as in_file, open(
        os.path.join('extract', file_name + ".GGA.txt"), mode="w"
    ) as out_gga, open(os.path.join('extract', file_name + ".GLL.txt"), mode="w") as out_gll, open(
        os.path.join('extract', file_name + ".GSA.txt"), mode="w"
    ) as out_gsa, open(
        os.path.join('extract', file_name + ".GSV.txt"), mode="w"
    ) as out_gsv, open(
        os.path.join('extract', file_name + ".RMC.txt"), mode="w"
    ) as out_rmc, open(
        os.path.join('extract', file_name + ".VTG.txt"), mode="w"
    ) as out_vtg:

        first_row_flag = {
            "GGA": True,
            "GLL": True,
            "GSA": True,
            "GSV": True,
            "RMC": True,
            "VTG": True,
        }

        for line in in_file:
            msg = line.split(";")

            if msg[3] == "GGA":
                if first_row_flag["GGA"]:
                    out_gga.write(
                        "date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7;field8;field9;field10;field11;field12;field13;field14\n"
                    )
                    first_row_flag["GGA"] = False
                out_gga.write(line)

            if msg[3] == "GLL":
                if first_row_flag["GLL"]:
                    out_gll.write("date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7\n")
                    first_row_flag["GLL"] = False
                out_gll.write(line)

            if msg[3] == "GSA":
                if first_row_flag["GSA"]:
                    out_gsa.write(
                        "date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7;field8;field9;field10;field11;field12;field13;field14;field15;field16;field17\n"
                    )
                    first_row_flag["GSA"] = False
                out_gsa.write(line)

            if msg[3] == "GSV":
                if first_row_flag["GSV"]:
                    out_gsv.write("date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7;field8\n")
                    first_row_flag["GSV"] = False
                out_gsv.write(line)

            if msg[3] == "RMC":
                if first_row_flag["RMC"]:
                    out_rmc.write(
                        "date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7;field8;field9;field10;field11;field12;field13\n"
                    )
                    first_row_flag["RMC"] = False
                out_rmc.write(line)

            if msg[3] == "VTG":
                if first_row_flag["VTG"]:
                    out_vtg.write(
                        "date;time;talker;msg_type;field1;field2;field3;field4;field5;field6;field7;field8;field9\n"
                    )
                    first_row_flag["VTG"] = False
                out_vtg.write(line)
