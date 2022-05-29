import re
import collections

def padFiles(src_file_1, src_file_2):
    
    with open(src_file_1, "r") as f1, open(src_file_2, "r") as f2:
        list_1 = f1.read().splitlines()
        list_2 = f2.read().splitlines()

    list_pairs_1 = {}
    list_pairs_2 = {}
 
    for item_1 in list_1:
        str_1 = re.sub(r'\t',' ',item_1)
        pair_1 = str_1.split(" ")[0:2]
        list_pairs_1[pair_1[1]] = pair_1[0]

    for item_2 in list_2:
        str_2 = re.sub(r'\t',' ', item_2)        
        pair_2 = str_2.split(" ")[0:2]
        list_pairs_2[pair_2[1]] = pair_2[0]
    
    for key_1 in list_pairs_1.keys():
        if key_1 not in list_pairs_2:
            list_pairs_2[key_1] = 0
    for key_2 in list_pairs_2.keys():
        if key_2 not in list_pairs_1:
            list_pairs_1[key_2] = 0

    print(list_pairs_1, list_pairs_2)
    sorted_list_1 = collections.OrderedDict(sorted(list_pairs_1.items()))
    sorted_list_2 = collections.OrderedDict(sorted(list_pairs_2.items()))
        
    with open(src_file_1 + "Padded", "w") as f1, open(src_file_2 + "Padded", "w") as f2:
        for key_1,key_2 in zip(sorted_list_1.keys(), sorted_list_2.keys()):
            try:
                f1.write("{0} {1}\n".format(int(sorted_list_1[key_1]), str(key_1)))
                f2.write("{0} {1}\n".format(int(sorted_list_2[key_2]), str(key_2)))
            except ValueError as e:
                print("Error: Confirm format of input file.")
                exit()
