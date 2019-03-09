import os


def WriteAds(ad_dict, filename):  # Writes ads from given dictionary to given file
    file = open(filename, 'a')
    old_ad_dic = ReadAds('../Files,Databa/Recorded Ads')
    i = 0
    for ad_id in ad_dict:
        if ad_id not in old_ad_dic:
            try:
                file.write(str(ad_id))
                file.write(str(ad_dict[ad_id]) + "\n")
            except:
                print("[Error] Unable to write ad("+str(i)+'.')
        i += 1
    file.close()


def ReadAds(filename):  # Reads given file and creates a dict of ads in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    ad_dict = {}
    with open(filename, 'r') as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{')
                ad_id = line[:index]
                dictionary = line[index:]
                dictionary = ast.literal_eval(dictionary)
                ad_dict[ad_id] = dictionary
    return ad_dict

