import urllib.request 
import requests
import time

def _get_download_link(html):
    html_list = str(html).split()
    for item in html_list:
        if ".zip" in item:
            if "href" in item:
                item = item.split('="', )[1].split('"')[0]
                return "https://nl.yamaha.com" + item
    
def _get_name_and_version(html):
    html_list = str(html).split("h1")
    h1 = html_list[1].strip("<>/")
    name, version = h1.split(" V")
    return name, version

def _get_info(device: str, max_retries=4, delay=1):
    remote = False
    if "remote" in device.lower():
        remote = True
        url = f"https://nl.yamaha.com/nl/support/updates/{device}.html"
    else:
        url = f"https://nl.yamaha.com/nl/support/updates/{device}_firm.html"
        
    print(url)
    for attempt in range(max_retries):
        try:
            request_url = urllib.request.urlopen(url)
            html = request_url.read()
            link = _get_download_link(html)
            name, version = _get_name_and_version(html)
            
            if remote:
                split = version.split(maxsplit=1)
                version = split[0]
                name = f"{name} {split[1]}"
                
            return name, version, link
        except Exception as e:
            # print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                return None

class _Devices:
    PM_SERIES: str = "rivage_pm"
    CL5: str = "cl5"
    CL3: str = "cl3"
    CL1: str = "cl1"
    QL5: str = "ql5"
    QL1: str = "ql1"
    DM7: str = "dm7"
    DM3: str = "dm3"
    TF_SERIES: str = "tf531_tf_rack"
    RIO3224_D2: str = "rio3224-d2"
    RIO1608_D2: str = "rio1608-d2"
    RIO3224_D: str = "rio3224-d"
    RIO1608_D: str = "rio1608-d"
    TIO1608_D: str = "tio1608-d"
    RO8_D: str = "ro8-d"
    RI8_D: str = "ri8-d"
    RSIO64_D: str = "rsio64-d"
    R_REMOTE_MAC: str = "r_remote_mac"
    R_REMOTE_WIN: str = "r_remote_win"
    
    @classmethod
    def list_all(cls):
        """Returns a list of all device values defined in the class."""
        return [value for name, value in cls.__dict__.items() if name in cls.__annotations__]


class YamahaFirmware():
    Devices = _Devices
    
    def get_info(device):
        return _get_info(device=device)

    def get_info_all(return_json: bool = True):
        device_list = _Devices.list_all()
        if return_json:
            all_list = {}
            for device in device_list:
                info = _get_info(device)
                json = {
                    "name": info[0],
                    "version": info[1],
                    "link": info[2]
                }
                # Use device as a unique key in all_list
                all_list[device] = json
        else:
            all_list = []
            for device in device_list:
                all_list.append(_get_info(device))
                
        return all_list
    
    def download_firmware(device, folder: str = "", optional_filename: str = ""):
            
        info = _get_info(device)
        url = info[2]
        
        if optional_filename == "":
            name = info[0].replace(" ", "_")+"_V"+info[1].replace(".", "-")
        else:
            name = optional_filename
            
        if folder == "":
            file_name = "./" + name
        elif folder != "":
            if folder.endswith("/"):
                file_name = folder + name
            else:
                file_name = folder + "/" + name
                
        file_name = file_name + ".zip"
            
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Open a local file in write-binary mode and write the content
            with open(file_name, "wb") as file:
                file.write(response.content)
            print("Download completed successfully.")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")


if __name__ == "__main__":
    # json = YamahaFirmware.get_info_all()
    # print(json["cl5"])
    # print(YamahaFirmware.get_info_all())
    # list = YamahaFirmware.Devices.list_all()
    # print(list)
    # YamahaFirmware.download_firmware(YamahaFirmware.Devices.PM_SERIES)
    print(YamahaFirmware.get_info(_Devices.CL5))