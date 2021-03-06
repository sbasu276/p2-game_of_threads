import sys, os

PAGE_SIZE = 4096 #Bytes
KEY_VALUE_SIZE = 16 #Bytes

#Set this based on your machine
BLOCK_SIZE_BYTES = 128 #Should be at the granularity of PAGE_SIZE
BLOCK_SIZE_KEYS = int(BLOCK_SIZE_BYTES/KEY_VALUE_SIZE) #Should be at the granularity of PAGE_SIZE

C1_FILE = 'C1.txt' #Main SSTable file name

index_table = []

class Request:
    def __init__(self, key=None, value=None, ifDel=None, fd=None):
        self.key = key
        self.value = value
        self.ifDel = ifDel #'D' if the key needs to be deleted

class C1:
    def __init__(self, f_name):
        self.f_name = f_name
        self.fd = None

    def init(self):
        self.fd = open(f_name, 'w')


    def merge(self, memtable):
    	"""Generates a new merged file with the same name as fd + .tmp extension\
        TODO: Replace the .txt file with the .tmp file"""

        temp_file_name = self.fd.name.strip('.txt')+'.tmp'
        temp_file = open(temp_file_name, 'w+')
        i = 0
        index = 0
        new_index_table = []
        for line in self.fd:
        old_entry = Request(line.split(' ')[0], line.split(' ')[1])
        while(i < len(c0_list)):
            new_entry = c0_list[i]
            if(new_entry.key > old_entry.key):
                temp_file.write(make_string(old_entry.key, old_entry.value))
                index += 1
                break
            elif(new_entry.key < old_entry.key):
                i += 1
                if(new_entry.ifDel != 'D'): #add to file if it is not a delete request
                temp_file.write(make_string(new_entry.key, new_entry.value))
                index += 1
            else:	# both keys are equal - Dedup
                i += 1
                if(new_entry.ifDel == 'D'):
                    #print('Deleting '+new_entry.key)
                    break
                else:
                    temp_file.write(make_string(new_entry.key, new_entry.value))
                    index += 1
                if(i == len(c0_list)):
                    break

        for line in self.fd:
            #print('Writing '+line)
            temp_file.write(line)	

        while(i < len(c0_list)):
            new_entry = c0_list[i]
            i += 1
            if(new_entry.ifDel != 'D'):
                temp_file.write(make_string(new_entry.key, new_entry.value))

        temp_file.close()
def make_string(key, value):
    line = key+' '+value
    if(len(line) < 16):
	i = 15 - len(line)
	while(i > 0):
            line += ' '
            i -= 1
    return line[:15]+'\n'

def init_c1_file():
	my_dict = {}
	names_fd = open('names.txt', 'r+')
	fd = open('C1.txt', 'w')
	for line in names_fd.readlines():
		line = line.strip('\n').split(' ')
		my_dict[line[0]] = line[1]	

	for key in sorted(my_dict):
		line = make_string(key, my_dict[key])
		fd.write(line)
	fd.close()

def gen_index_table(fd):
	global index_table 
	index_table= []
	offset = 0
	fd.seek(0, 0)
	file_size = os.path.getsize(fd.name)
	while (offset < file_size):
		line = fd.readline()
		items = line.strip('\n ').split(' ')
		index_table.append((items[0], offset))
		offset += BLOCK_SIZE_BYTES
		fd.seek(offset, 0)

def get_key_it(a):
	return a[0]

def get_key_sst(a):
	return a.strip('\n ').split(' ')[0]

def binarySearch(arr, l, r, x, extract_key): 
	while l <= r: 
		mid = int(l + (r - l)/2);
		arr_mid = extract_key(arr[mid])
		if arr_mid == x: 
			return mid 
		elif arr_mid < x: 
			l = mid + 1
		else: 
			r = mid - 1
	return r

def islice(fd, offset, numLines):
	lines = []
	fd.seek(offset, 0)
	for i in range(numLines):
		line = fd.readline().strip('\n ')
		if line:
			lines.append(line)
	return lines

def get(fd, key):
	r = binarySearch(index_table, 0, len(index_table)-1, key, get_key_it)
	search_block = islice(fd, index_table[r][1], BLOCK_SIZE_KEYS)
	r = binarySearch(search_block, 0, len(search_block)-1, key, get_key_sst)
	if(get_key_sst(search_block[r]) == key):
		return search_block[r].strip('\n ').split(' ')[1]
	else:
		return None


if __name__ == "__main__":

	init_c1_file() #use to init C1 file

	fd = open('C1.txt', 'r')

	gen_index_table(fd) #generate index table

	#testing presence of all the keys of names.txt in C1.txt
	my_fd = open('names.txt', 'r')
	for line in my_fd.readlines():
		line = line.strip('\n ').split(' ')
		value = get(fd, line[0])
		if(value):
			#print('Key found!')
			continue
		else:
			print('Key '+line[0]+' not found!')
			exit()

	#testing merging
	fd.seek(0, 0)
	c0_list = []
	c0_list.append(Request('Aarav', 'Ruth')) #inserting a new key at the beginning of the file
	c0_list.append(Request('Aman', 'Jain')) #inserting a new entry in the middle
	c0_list.append(Request('Novak', 'Dvic', 'D')) #deleting a non-existent key
	c0_list.append(Request('Tonia', 'Jain', 'D'))	#deleting an existing entry
	c0_list.append(Request('Warren', 'Jain', 'W')) #Adding an entry
	c0_list.append(Request('Zzaid', 'Moph', '')) #Adding an entry at the end of file
	merge(fd, c0_list)

	
