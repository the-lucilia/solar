"""
Project Solar! This is a basic data analyst script meant to allow the user to gather information on NS regions' WA -
membership rates as well as who is endorsing who etc.

Patch Notes v0.2: Rewrote entire thing to make use of functions to allow different options for the user -M
Patch Notes v0.1.2: Added functionality to show non-endorsers for officers -A
"""
import requests
from xml.etree import ElementTree as et
residents = []
wa_nations = []


def region_info(headers, choice, region=None):
    residents.clear()
    wa_nations.clear()
    if region is None:
        region = str(input("Please enter the target region: ")).lower().replace(" ", "_")
    # Get all wa nations
    wa_residents = requests.get(
        f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=wanations",
        headers=headers,
    )
    wa_nations_root = et.fromstring(wa_residents.content)
    wa = wa_nations_root.find("UNNATIONS").text.split(",")
    # Appends the global scope list with all WA nations!
    for nat in wa:
        wa_nations.append(nat)

    # Gets same info as above but for all nations, not just WA!
    all_residents = requests.get(
        f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=nations",
        headers=headers,
    )
    all_residents_root = et.fromstring(all_residents.content)
    ar = all_residents_root.find("NATIONS").text.split(":")
    for nat in ar:
        residents.append(nat)

    match choice:
        case "ner":
            print("For Non-Endorsing Delegate and Officers:")
            calc_non_endos(headers, region)
        case "nwr":
            print("For Non-WA in Region:")
            calc_non_wa(region)
        case _:
            print("For Non-Endorsing Nation:")


def calc_non_endos(headers, region):
    residents_len = len(wa_nations)
    # Get delegate info
    delegate_name = requests.get(
        f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=delegate+officers",
        headers=headers,
    )
    delegate_name_root = et.fromstring(delegate_name.content)
    delegate = delegate_name_root.find("DELEGATE").text
    # Get officers info
    officers = delegate_name_root.find("OFFICERS").findall("OFFICER")
    # Endo info
    delegate_endos = requests.get(
        f"https://www.nationstates.net/cgi-bin/api.cgi?nation={delegate}&q=endorsements",
        headers=headers,
    )
    delegate_endos_root = et.fromstring(delegate_endos.content)
    endorsements = delegate_endos_root.find("ENDORSEMENTS").text.split(",")
    endorsers = [endorsement for endorsement in endorsements]
    non_endorsing = [nation for nation in wa_nations if nation not in endorsers and nation != delegate]
    non_endo_len = len(non_endorsing)
    endo_percent = (non_endo_len * 100) / residents_len
    print(f"The following nations are not endorsing {delegate}: {non_endorsing} ({non_endo_len} nation(s))")
    print(
        f"Of all {residents_len} WA Nations in {region} there are {endo_percent:.2f}% WA nations "
        f"are not endorsing delegate {delegate}.")
    print("")
    # Runs through all the officers
    for officer in officers:
        officer_nation = officer.find("NATION").text
        if officer_nation == delegate:
            continue  # Skip the delegate

        officer_endos = requests.get(
            f"https://www.nationstates.net/cgi-bin/api.cgi?nation={officer_nation}&q=wa+endorsements", headers=headers)
        officer_endos_root = et.fromstring(officer_endos.content)
        if officer_endos_root.find("UNSTATUS").text == "Non-member":
            print(f"{officer_nation} is not in the WA!")
            print()
            continue

        if officer_endos_root.find("ENDORSEMENTS").text and "," in officer_endos_root.find("ENDORSEMENTS").text:
            endorsements = officer_endos_root.find("ENDORSEMENTS").text.split(",")
        else:
            print(f"Error: No endorsements for {officer_nation}")
            print()
            continue

        endorsers = [endorsement for endorsement in endorsements]
        non_endorsing = [nation for nation in wa_nations if nation not in endorsers and nation != officer_nation]
        non_endo_len = len(non_endorsing)
        endo_percent = (non_endo_len * 100) / residents_len

        print(f"The following nations are not endorsing {officer_nation}: {non_endorsing} ({non_endo_len} nation(s))")
        print(
            f"Of all {residents_len} WA Nations in {region} there are {endo_percent:.2f}% WA nations not "
            f"endorsing officer {officer_nation}.")
        print("")


def calc_non_nat(headers):
    nation = str(input("Please enter the target nation: ")).lower().replace(" ", "_")
    nation_info = requests.get(f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=region+wa+endorsements",
                               headers=headers)
    nation_info_root = et.fromstring(nation_info.content)
    if nation_info_root.find("UNSTATUS").text == "WA Member":
        nation_region = nation_info_root.find("REGION").text
        region_info(headers, "_", nation_region)
        wa_length = len(wa_nations)
        nation_endorsements = nation_info_root.find("ENDORSEMENTS").text
        non_endorsers = [nation for nation in wa_nations if nation not in nation_endorsements]
        non_endo_len = len(non_endorsers)
        non_endo_percent = non_endo_len * 100 / wa_length
        print(f"The following nations are not endorsing {nation}: {non_endorsers} ({non_endo_len} nation(s))")
        print(f"Of the total {wa_length} nations in {nation_region} there are {non_endo_percent:.2f}% nations not "
              f"endorsing {nation}")
    else:
        print(f"{nation} is not a member of the WA!")


def calc_non_wa(region):
    res_length = len(residents)
    non_wa = [nat for nat in residents if nat not in wa_nations]
    non_length = len(non_wa)
    non_percent = non_length * 100 / res_length
    print(f"The following nations are not in the WA in {region}: {non_wa} ({non_length} nation(s))")
    print(f"Of all {res_length} nations in {region} there are {non_percent:.2f}% nations not in the WA")


def display_options():
    print("Find non-endorsers within the region for delegate and regional officers (NER)")
    print(f"Find non-endorsers within the region for the target nation (NEN)")
    print(f"Get a list of all non-WA nations in a target region (NWR)")
    print(f"Restate the options (OPT)")
    print(f"And exit will exit (exit)!")


def main():
    # User agent input
    user_input = (
        input("Please enter your main nation for the User-Agent: ")
        .lower()
        .replace(" ", "_")
    )
    # Headers
    headers = {
        "User-Agent": f"Project Solar requesting region and nation information, deved by nation=Hesskin_Empire "
                      f"and in use by {user_input}"
    }
    print(f"Hello, {user_input}! Thank you for your interest in solar! There are a few things you can do with solar so"
          f"please choose one from the list: ")
    display_options()
    user_choice = str(input("What would you like to do? ")).lower()
    while user_choice != 'exit':
        match user_choice:
            case "ner":
                region_info(headers, user_choice)
            case "nen":
                calc_non_nat(headers)
            case "nwr":
                region_info(headers, user_choice)
            case "opt":
                display_options()
            case _:
                print(f"I'm sorry, {user_input} but {user_choice} is not a valid choice. Please try again!")
        user_choice = str(input("What would you like to do? ")).lower()


if __name__ == "__main__":
    main()
    input("Press enter to exit. . .")
