import sys, os, csv, operator, time, json, http.server, socketserver

def Main():
	args = []
	fileType = check_filetype(sys.argv[2])
	args=read_csv()
	print("args:", len(args), len(args[0]))

	try:
		result=sorted(get_intersected(*args[:4]), key=operator.itemgetter('score'), reverse=True)
	except:
		print('*****')
		print("ERROR: Dataset is of an invalid format or the symbol was not found")
		print('*****')
		exit()
	# print(result)
	result = set_depth(result, *args)
	try: 
		array = list(map(operator.itemgetter('root_symbol', 'cor_symbol'), result))
		if not len(result):
			print("Graph is empty! Selected symbol: " + args[0] + " does not have any relationships!")
	except:
		return "error with "
	save_results(array, "output/cluster/", "cluster_output.json")
	save_results(result, "output/graph/", "graph_output_full.json")
	return

def set_depth(result, root_symbol, headers, data, min_score, max_depth, branches, nodes, n_headers, n_data, t_headers, t_data):
	#initialize 2 lists containing symbols
	symbols=[]
	covered_symbols=[]
	temp=[]
	count=0
	covered_symbols.append(root_symbol)

	#this is used for the while loop(subtracted by 1 because first level has already been covered above)
	remainer_depth=max_depth-1

	while remainer_depth>0 and len(result)<nodes:
		if count%2==1:
			data=n_data.copy()
			headers=n_headers[:]
		else:
			data=t_data.copy()
			headers=t_headers[:]

		#removes all symbols previously covered
		symbols=[x for x in symbols if x not in covered_symbols]
		for j in range(len(result)):
			#checking if the symbol in question has already been covered or not
			if(result[j]['cor_symbol'] not in covered_symbols and result[j]['cor_symbol'] not in symbols):
				symbols.append(result[j]['cor_symbol'])
		#print("Symbols: ", symbols)
		
		temp[:]=[]
		try:
			for name in symbols:
				#performs the same function as with the root symbol
				temp[(len(temp)):]=get_intersected(name, headers, data, min_score, max_depth-remainer_depth+1)
		except:
			pass
		remainer_depth-=1


		temp=sorted(sorted(temp, key=operator.itemgetter('score'), reverse=True), 
			key=operator.itemgetter('depth'))

		#updates symbols already covered
		covered_symbols.extend(symbols)
		temp=remove_duplicates(temp)
		if branches>0:
			temp=set_branches(temp, branches, covered_symbols)

		result.extend(temp)


		count+=1

	return result

def save_results(list, path, name):
	timestring= time.strftime("%Y%m%d-%H%M%S")
	full=path+timestring+"_"+name
	if not os.path.exists(os.path.dirname(path)):
		try:
			os.makedirs(os.path.dirname(path))
		except:
			print("exception")

	with open(full, 'w') as outfile:
		json.dump(list, outfile, indent=2)
	return 1

def check_filetype(filename):
	delim= None
	
	if filename[-4:]=='.csv':
		return ','
	elif filename[-4:]=='.tsv':
		return '\t'
	else:
		print('*****')
		print('ERROR: Passed dataset is not a supported file. Use Comma-Seprated Values(.csv) or Tab-Seperated Values(.tsv) files')
		print('*****')
		exit()


#this function gets all the correlated symbols of the root symbol
def get_intersected(symbol, headers, dict, min_score, depth=1):
	print(symbol)
	return [{'root_symbol':symbol, 'cor_symbol':headers[i].strip(), 'score':score, 'depth':depth} for i,
	score in enumerate(dict[symbol]) if score > min_score and headers[i].strip()!=symbol]


def read_csv():
	if len(sys.argv) != 3:
		print('*****')
		print('Usage: python main.py <nodes> <file_name>')
		print('Example: python main.py AGIO 50 datasets/pharma_pharma_dataset.csv')
		print('*****')
		exit()
	# else:
	# 	try:
	# 		write_labels(sys.argv[2])
    #         # print(args)
	# 	except:
	# 		print('*****')
	# 		print('Usage: python main.py <nodes> <file_name>')
	# 		print('Example: python main.py 50 datasets/pharma_pharma_dataset.csv')
	# 		print('Note: passing the argument for branches and nodes as 0 gives the max possible amount of nodes and branches')
	# 		print('Run with only the dataset as argument to generate a list of the labels')
	# 		print('*****')
	# 		exit()
	
	nodes = int(sys.argv[1])
	file_name = sys.argv[2]

	sys.argv = [sys.argv[0]]
	min_score=0.0001
	if nodes>100:
		nodes=100

	#Read the dataset
	headers = []
	data = {}
	n_headers = []
	n_data = {}
	t_headers = []
	t_data = {}

	delim=check_filetype(file_name)

	with open(file_name) as file:
		csv_reader = csv.reader(file, delimiter=delim)
		headers = next(csv_reader)[1:]
		n_headers = headers[:]
		for row in csv_reader:
			temp=row[0].rstrip()
			data[temp] = [float(x) for x in row[1:]]
		n_data = data.copy()
	try:
		# data[header[0]]
		t_headers=n_headers
		t_data=n_data
	except:
		with open(file_name) as file:
			t_csv=csv.reader(file, delimiter=delim)
			t_csv=zipper(t_csv)
			t_headers = next(t_csv)[1:]
			for row in t_csv:
				temp=row[0].rstrip()
				t_data[temp] = [float(x) for x in row[1:]]
	return "000227_sym", headers, data, min_score, 5, 5, nodes, n_headers, n_data, t_headers, t_data


def zipper(csv):
	if sys.version_info[0] < 3:
		from itertools import izip
		return izip(*csv)
	else:
		return zip(*csv)

def write_labels(filename):
	print("hi", filename)
	with open(filename) as file:
		delim=check_filetype(filename)
		print(delim)
		column_csv = csv.reader(file, delimiter=delim)
		print(column_csv)
		index_csv=None
		columns = next(column_csv)[1:]
		filename=filename.split('/', 1)[-1]
		filename=filename[:-4]
		print(filename)
		with open("labels/column_labels_"+filename+".txt", 'w') as column_file:
			column_file.writelines("%s\n" % column for column in columns)

		index_csv=zipper(column_csv)

		rows = next(index_csv)[:]
		with open("labels/row_labels_"+filename+".txt", 'w') as index_file:
			index_file.writelines("%s\n" % row for row in rows)
		print('*****')
		print('Labels saved to "row_labels_'+filename+'.txt" and "column_labels_'+filename+'.txt" in the folder "labels"')
		print('*****')
		os._exit(1)


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'src/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


if __name__ == '__main__':
	# Create an object of the above class
	handler_object = MyHttpRequestHandler

	PORT = 3000
	my_server = socketserver.TCPServer(("", PORT), handler_object)
	Main()
	# Star the server
	my_server.serve_forever()
	
exit()
