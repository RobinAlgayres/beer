import sys
import numpy as np
# takes output from BEER with and split it into separate onehot format for submission : 
# in:
# 0107_400123_0000 au12 au33 au33 au56 au56
# 0107_400123_0002 au18 au33 au55 au55 au58
# out:
# 0107_400123_0000.txt
#     0 0 0 0 0 0 1 0 0
#     0 0 0 0 0 1 0 0 0
#     0 0 0 0 0 1 0 0 0
#     0 1 0 0 0 0 0 0 0
#     0 0 0 1 0 0 0 0 0

print("init raw text file:",sys.argv[1]," dest folder:",sys.argv[2])

txt_file=sys.argv[1]
dest_dir=sys.argv[2]
with open(txt_file, 'r') as myfile:
    data=myfile.read()
data_array=data.split('\n')

aud_number=100 #BEER produces 100 different phonemes
onehot=np.zeros((aud_number,),dtype=int) 
for w in range(len(data_array)):
    w_split= data_array[w].split(' ')
    filename = w_split[0]+'.txt'
    w_split=w_split[1:] #getting rid of sentence id
    sentence=''
    for i in range(len(w_split)):
        indice=int(w_split[i].split('u')[1])-1
        onehot[indice]=1
        sentence+=' '.join([str(x) for x in onehot])+'\n'
        onehot[indice]=0    
#    text_corpora+=sentence+' '
    with open(dest_dir+'/'+filename, 'w') as myfile:
        myfile.write(sentence) 

#text_corpora+='\n'
#with open(text_corpora_path,'w') as myfile:
#        myfile.write(text_corpora)
                                                            
