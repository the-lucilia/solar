import requests
from xml.etree import ElementTree as et

User_Input = (
    input("Please enter your main nation for the User-Agent: ")
    .lower()
    .replace(" ", "_")
            )
headers = {
    "User-Agent": f"Project Solar requesting region and nation information, deved by nation=Hesskin. {User_Input} using"
          }

region = input("Please enter target region: ")
delegate_name = requests.get(
    f"https://www.nationstates.net/cgi-bin/api.cgi?region={region.lower().replace(' ','_')}&q=delegate",
    headers=headers,
)
wa_nations = requests.get(
    f"https://www.nationstates.net/cgi-bin/api.cgi?region={region.lower().replace(' ','_')}&q=wanations",
    headers=headers,
)

wa_nations_root = et.fromstring(wa_nations.content)
wa = wa_nations_root.find("UNNATIONS").text.split(",")

delegate_name_root = et.fromstring(delegate_name.content)
Delegate = delegate_name_root.find("DELEGATE").text
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
