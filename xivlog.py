import json
import os
import re
import sys
from pprint import pprint

import pandas as pd
import requests

FIGHT_TABLE = 'https://www.fflogs.com/reports/fights-and-participants/{id}/0'
# SUMMARY_GRAPH = 'https://www.fflogs.com/reports/summary-graph/{log_id}/2/{start_time}/{end_time}/0/0/Any/0/-1.0.-1/0'
# TABLE_URL = "https://www.fflogs.com/reports/{table_type}/{log_id}/2/{start_time}/{end_time}/0/0/Any/0/-1.0.-1/0"
DAMAGE_DONE = "https://www.fflogs.com/reports/graph/{table_type}/{log_id}/{fight}/{start_time}/{end_time}/source/0/0/0/0/0/0/-1.0.-1/0/Any/Any/0/0"

def header():
    bar = "==========================================================="
    header = r"""
       ________            __         ______           
      / _/ _/ /__  ___ _  / /____    / _/ _/_______  __
     / _/ _/ / _ \/ _ `/ / __/ _ \  / _/ _/ __(_-< |/ /
    /_//_//_/\___/\_, /  \__/\___/ /_//_/ \__/___/___/ 
                 /___/                                           
"""
    print(bar)
    print(header)
    print(bar)

def bar():
    print("------------------------------------")
    
def generate_log_info_from(log_url):
    info = {}
    id_regex = re.compile(r"(?<=reports\/)[a-zA-Z\d]*(?=#)")
    fight_regex = re.compile(r"(?<=fight=).*[\d]")
    type_regex = re.compile(r"(?<=type=).*[a-zA-Z]")
    info_id = id_regex.match(log_url).group()
    info_temp = log_url.split("#")[1].split("&")
    info['id'] = info_id
    for i in info_temp:
        parse_i = i.split("=")
        info[parse_i[0]] = parse_i[1]
    return info

def fetch_damage_done_json_from(log_info):
    fights = requests.get(FIGHT_TABLE.format(id=log_info['id'])).json().get('fights')
    fight = fights[int(log_info['fight'])-1]
    start_time = fight.get('start_time')
    end_time = fight.get('end_time')
    damage_done = requests.get(DAMAGE_DONE.format(
        table_type=log_info['type'] if log_info['type'] else 'damage-done',
        log_id=log_info['id'],
        fight=log_info['fight'],
        start_time=start_time,
        end_time=end_time)).json()
    return damage_done

def print_fight_option(fights):
    
    pass

def print_source_option(damage_donw_json):
    cls()
    header()
    print("Choose the source you want to export.", end="\n\n")
    template = "{index} => {name}"
    for index, data in enumerate(damage_donw_json['series']):
        print(template.format(index=index, name=data['name']))
    print("x => Back to top")
    bar()

def generate_damage_timeline_in_json_by(source):
    data = source['data']
    timeline = []
    for time, damage in enumerate(data):
        dps_node = {}
        dps_node['time'] = time * source.get('pointInterval')
        dps_node['damage'] = damage
        timeline.append(dps_node)
    return timeline

def dump_json_to_csv(timeline, name):
    df = pd.DataFrame(timeline)
    df = df[['time', 'damage']]
    if not os.path.exists("./output"):
        os.system("mkdir output")
    df.to_csv("./output/{filename}.csv".format(filename=name))

def generate_filename(source):
    name = str(source.get('name'))
    return name.replace(" ", "_")

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    NOTICE = "Enter fflogs id or \"x\" to exit."
    while True:
        cls()
        header()
        print(NOTICE)

        log_url = input("Log id: ")
        if log_url is "x":
            os._exit(0)

        try:
            log_info = generate_log_info_from(log_url)
        except AttributeError:
            NOTICE = "Can't find the log, Please check the ID again."
            continue

        damage_done = fetch_damage_done_json_from(log_info)

        print_source_option(damage_done)

        source_index = input("Source index:")
        if source_index is "x":
            NOTICE = "Enter fflogs id or \"x\" to exit."
            continue

        source = damage_done['series'][int(source_index)]
        time_line_json = generate_damage_timeline_in_json_by(source)
        dump_json_to_csv(time_line_json, generate_filename(source))
        NOTICE = "DONE!"

if __name__ == "__main__":
    main()
