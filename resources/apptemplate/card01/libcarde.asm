macro WAIT frames
	db D3h,{frames}
mend

macro API number
	rst 0h
	db {number}
mend

macro APIEXT number
	rst 8h
	db {number}
mend

