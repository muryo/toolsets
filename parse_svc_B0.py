import	sys
import	re

current_header = [] # represents sets of one component's freqs name got from svc spec, such as ACPP8 (1386)
all_pp_list = [] # represents all components' freqs name set
svc_table = {}
all_volt_set = [] # it contains 16 voltage set for corresponding profile

def process_line(line):
	global current_header, all_pp_list, svc_table
	l = line.split(",")
	if l[0] == "Profile": # if it is the table header(freqs' name)
		current_header = []
		i = 2
		while i < len(l):
			if l[i] != "":
				current_header.append(l[i])
				all_pp_list.append(l[i])
				svc_table[l[i]] = {}
			i += 4
	if l[0].isdigit() and int(l[0]) in range(0,16): # it is the table content(vmin value)
		for i in range(0, len(current_header)):
			svc_table[current_header[i]][l[0]] = l[2 + i*4 + 1]

def adjust_volt_table(): # remove some voltage when len(volt_set) exceed 16
	all_volt_set[11].remove(962500)
	return

def gen_volt_map_table():
	global svc_table, all_pp_list, all_volt_set

	for profile in range(0, 16):
		for pp in all_pp_list:
			volt = svc_table[pp][str(profile)]
			if volt == "":
				svc_table[pp][str(profile)] = svc_table[pp][str((profile+1)%16)]
	# convert string to number
	for profile in range(0, 16):
		for pp in all_pp_list:
			svc_table[pp][str(profile)] = int(1000 * float(svc_table[pp][str(profile)]))


	for profile in range(0, 16):
		volt_set = set()
		for pp in all_pp_list:
			volt = svc_table[pp][str(profile)]
			volt_set.add(volt)
		volt_set = list(volt_set)
		volt_set.sort()
	#	volt_set.insert(0, 950000) # level 0 rsvd for D1
		all_volt_set.append(volt_set)
	#	print "profile: %d len: %d" % (profile, len(volt_set))
	#	print volt_set

#	adjust_volt_table() # adjust volt_table when len(volt_set) exceed 16
	for i in range(0, 16):
		while len(all_volt_set[i]) < 16:
			all_volt_set[i].append(all_volt_set[i][len(all_volt_set[i])-1])
	for profile in range(0, 16):
		print "/* Profile: " + str(profile) + " */"
		print "{"
		i = 0
		print "\t",
		while i < 16:
			sys.stdout.write(str(all_volt_set[profile][i]) + ",")
			if i == 15:
				print
			elif (i+1) % 4 == 0:
				print
				print "\t",
			else:
				if int(all_volt_set[profile][i]) < 1000000:
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "},"

def gen_freqs_cmb_table():
	global all_volt_set, svc_table, all_pp_list
	print " ********* Start to generate freqs_cmb table for all profile ********* "

	for profile in range(0, 16):
		cpu = {}
		axi = {}
		ddr = {}
		gc2d = {}
		gc3d = {}
		dec = {}
		enc = {}
		cpu_pattern = re.compile(r'ACPP')
		axi_pattern = re.compile(r'AXPP')
		ddr_pattern = re.compile(r'DPP')
		gc2d_pattern = re.compile(r'G2PP')
		gc3d_pattern = re.compile(r'G3PP')
		dec_pattern = re.compile(r'VDPP')
		enc_pattern = re.compile(r'VEPP')
#		print all_volt_set[profile]
		print "\t/* Profile: %d */" % profile
		print "\t[%d] = {" % profile
		for i in range(0, 16):
		#	print "volt: %d" % all_volt_set[profile][i]
			for pp in all_pp_list:
				if all_volt_set[profile][i] == svc_table[pp][str(profile)]:
					# for cpu
					if cpu_pattern.match(pp) and cpu.has_key(i) == False:
						cpu[i] = pp
					# for axi
					if axi_pattern.match(pp) and axi.has_key(i) == False:
						axi[i] = pp
					# for ddr
					if ddr_pattern.match(pp) and ddr.has_key(i) == False:
						ddr[i] = pp
					# for gc2d
					if gc2d_pattern.match(pp) and gc2d.has_key(i) == False:
						gc2d[i] = pp
					# for gc3d
					if gc3d_pattern.match(pp) and gc3d.has_key(i) == False:
						gc3d[i] = pp
					# for dec
					if dec_pattern.match(pp) and dec.has_key(i) == False:
						dec[i] = pp
					# for enc
					if enc_pattern.match(pp) and enc.has_key(i) == False:
						enc[i] = pp
		num_pattern = re.compile(r'\d{2,}')

		# for cpu
		for i in range(0, 16):
			if cpu.has_key(i) == False and cpu.has_key(i-1) == True:
				cpu[i] = cpu[i-1]
			elif cpu.has_key(i) == False and cpu.has_key(i-1) == False:
				cpu[i] = 0

		for i in range(0, 16):
			cpu_freq = num_pattern.findall(str(cpu[i]))
			if cpu_freq:
				cpu[i] = str(int(cpu_freq[0]) * 1000000)
			else:
				cpu[i] = "0"
		print "\t\t[CORE]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + cpu[i] + ",\t\t" + cpu[i+1] + ", \t" + cpu[i+2] + ", \t" + cpu[i+3]
			sys.stdout.write(cpu[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if cpu[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		# for axi
		for i in range(0, 16):
			if axi.has_key(i) == False and axi.has_key(i-1) == True:
				axi[i] = axi[i-1]
			elif axi.has_key(i) == False and axi.has_key(i-1) == False:
				axi[i] = 0

		for i in range(0, 16):
			axi_freq = num_pattern.findall(str(axi[i]))
			if axi_freq:
				axi[i] = str(int(axi_freq[0]) * 1000000)
			else:
				axi[i] = "0"
		print "\t\t[AXI]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + axi[i] + ",\t\t" + axi[i+1] + ", \t" + axi[i+2] + ", \t" + axi[i+3]
			sys.stdout.write(axi[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if axi[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"


		# for ddr
		for i in range(0, 16):
			if ddr.has_key(i) == False and ddr.has_key(i-1) == True:
				ddr[i] = ddr[i-1]
			elif ddr.has_key(i) == False and ddr.has_key(i-1) == False:
				ddr[i] = 0

		for i in range(0, 16):
			ddr_freq = num_pattern.findall(str(ddr[i]))
			if ddr_freq:
				ddr[i] = str(int(ddr_freq[0]) * 1000000)
			else:
				ddr[i] = "0"
		print "\t\t[DDR]\t= { 0,"	# ddr use hwdfc
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + ddr[i] + ",\t\t" + ddr[i+1] + ", \t" + ddr[i+2] + ", \t" + ddr[i+3]
			sys.stdout.write(ddr[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if ddr[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		# for gc2d
		for i in range(0, 16):
			if gc2d.has_key(i) == False and gc2d.has_key(i-1) == True:
				gc2d[i] = gc2d[i-1]
			elif gc2d.has_key(i) == False and gc2d.has_key(i-1) == False:
				gc2d[i] = 0

		for i in range(0, 16):
			gc2d_freq = num_pattern.findall(str(gc2d[i]))
			if gc2d_freq:
				gc2d[i] = str(int(gc2d_freq[0]) * 1000000)
			else:
				gc2d[i] = "0"
		print "\t\t[GC2D]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + gc2d[i] + ",\t\t" + gc2d[i+1] + ", \t" + gc2d[i+2] + ", \t" + gc2d[i+3]
			sys.stdout.write(gc2d[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if gc2d[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		# for gc3d
		for i in range(0, 16):
			if gc3d.has_key(i) == False and gc3d.has_key(i-1) == True:
				gc3d[i] = gc3d[i-1]
			elif gc3d.has_key(i) == False and gc3d.has_key(i-1) == False:
				gc3d[i] = 0

		for i in range(0, 16):
			gc3d_freq = num_pattern.findall(str(gc3d[i]))
			if gc3d_freq:
				gc3d[i] = str(int(gc3d_freq[0]) * 1000000)
			else:
				gc3d[i] = "0"
		print "\t\t[GC3D]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + gc3d[i] + ",\t\t" + gc3d[i+1] + ", \t" + gc3d[i+2] + ", \t" + gc3d[i+3]
			sys.stdout.write(gc3d[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if gc3d[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		# for dec
		for i in range(0, 16):
			if dec.has_key(i) == False and dec.has_key(i-1) == True:
				dec[i] = dec[i-1]
			elif dec.has_key(i) == False and dec.has_key(i-1) == False:
				dec[i] = 0

		for i in range(0, 16):
			dec_freq = num_pattern.findall(str(dec[i]))
			if dec_freq:
				dec[i] = str(int(dec_freq[0]) * 1000000)
			else:
				dec[i] = "0"
		print "\t\t[VPUDE]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + dec[i] + ",\t\t" + dec[i+1] + ", \t" + dec[i+2] + ", \t" + dec[i+3]
			sys.stdout.write(dec[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if dec[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		# for enc
		for i in range(0, 16):
			if enc.has_key(i) == False and enc.has_key(i-1) == True:
				enc[i] = enc[i-1]
			elif enc.has_key(i) == False and enc.has_key(i-1) == False:
				enc[i] = 0

		for i in range(0, 16):
			enc_freq = num_pattern.findall(str(enc[i]))
			if enc_freq:
				enc[i] = str(int(enc_freq[0]) * 1000000)
			else:
				enc[i] = "0"
		print "\t\t[VPUEN]\t= { 1,"
		i = 0
		print "\t\t",
		while i < 16:
#			print "\t\t" + enc[i] + ",\t\t" + enc[i+1] + ", \t" + enc[i+2] + ", \t" + enc[i+3]
			sys.stdout.write(enc[i] + ",")
			if (i+1) % 4 == 0:
				print
				print "\t\t",
			else:
				if enc[i] == "0":
					print "\t\t",
				else:
					print "\t",
			i += 1
		print "}, /* HZ */"

		print "\t},"
	return

if len(sys.argv) != 2:
	print "Usage: python %s input_file.csv > output" % sys.argv[0]
	exit(-1)

f = open(sys.argv[1])
l = f.readline()
while l != "":
	process_line(l)
	l = f.readline()
f.close()

#print svc_table
gen_volt_map_table()

gen_freqs_cmb_table()
