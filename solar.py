# Patch notes: Added functionality to show non-endorsers for officers

import requests
from xml.etree import ElementTree as et

User_Input = (
    input("Please enter your main nation for the User-Agent: ")
    .lower()
    .replace(" ", "_")
            )
# Headers
headers = {
    "User-Agent": f"Project Solar requesting region and nation information, deved by nation=Hesskin. {User_Input} using"
          }

region = input("Please enter target region: ")
delegate_name = requests.get( #Delegate
    f"https://www.nationstates.net/cgi-bin/api.cgi?region={region.lower().replace(' ','_')}&q=delegate+officers",
    headers=headers,
)
wa_nations = requests.get( #All WA nations
    f"https://www.nationstates.net/cgi-bin/api.cgi?region={region.lower().replace(' ','_')}&q=wanations",
    headers=headers,
)

wa_nations_root = et.fromstring(wa_nations.content)
wa = wa_nations_root.find("UNNATIONS").text.split(",") # List of WA nations

delegate_name_root = et.fromstring(delegate_name.content)
Delegate = delegate_name_root.find("DELEGATE").text #Delegate nation
Officers = delegate_name_root.find("OFFICERS").findall("OFFICER")

#for officer in Officers:
#    print(officer.find("NATION").text)

residents = [wa_nation for wa_nation in wa]
residents_len = len(residents)

delegate_endos = requests.get(
    f"https://www.nationstates.net/cgi-bin/api.cgi?nation={Delegate}&q=endorsements",
    headers=headers,
                             )
delegate_endos_root = et.fromstring(delegate_endos.content)
endorsements = delegate_endos_root.find("ENDORSEMENTS").text.split(",")

endorsers = [endorsement for endorsement in endorsements]
non_endorsing = [nation for nation in residents if nation not in endorsers and nation != Delegate]
non_endo_len = len(non_endorsing)
endo_percent = (non_endo_len * 100) / residents_len

print(f"The following nations are not endorsing {Delegate}: {non_endorsing} ({non_endo_len} nation(s))")
print(f"Of all {residents_len} WA Nations in {region} there are {endo_percent:.2f}% WA nations not endorsing delegate {Delegate}.")
print()

for officer in Officers:
    officerNation = officer.find("NATION").text
    if officerNation == Delegate:
        continue #Skip the delegate, we did that already

    officer_endos = requests.get(f"https://www.nationstates.net/cgi-bin/api.cgi?nation={officerNation}&q=wa+endorsements",headers=headers)
    officer_endos_root = et.fromstring(officer_endos.content)
    if officer_endos_root.find("ENDORSEMENTS").text and "," in officer_endos_root.find("ENDORSEMENTS").text:
        endorsements = officer_endos_root.find("ENDORSEMENTS").text.split(",")
    else:
        print(f"Error: No endorsements for {officerNation}")
        continue

    endorsers = [endorsement for endorsement in endorsements]
    non_endorsing = [nation for nation in residents if nation not in endorsers and nation != officerNation]
    non_endo_len = len(non_endorsing)
    endo_percent = (non_endo_len * 100) / residents_len

    print(f"The following nations are not endorsing {officerNation}: {non_endorsing} ({non_endo_len} nation(s))")
    print(f"Of all {residents_len} WA Nations in {region} there are {endo_percent:.2f}% WA nations not endorsing officer {officerNation}.")

