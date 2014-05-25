import pycurl
import cStringIO
import json
import recordaudio
import thread

from Tkinter import *

#buffer to store the responses in
buf = cStringIO.StringIO()

#settings
client_id       = {CLIENT_ID} # Replace this with your client id
client_secret   = {CLIENT_SECRET} # Replace this with your client secret
post_field_string = "client_id=" + client_id+ "&client_secret="+client_secret+"&grant_type=client_credentials&scope=SPEECH"

#create pycurl object
c = pycurl.Curl()

#First get the access tokens.
c.setopt(c.URL, "https://api.att.com/oauth/token")
c.setopt(c.HTTPHEADER, ['Accept: application/json', 'Content-Type: application/x-www-form-urlencoded'])
c.setopt(c.POSTFIELDS, post_field_string)
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()

#parse the response
jsonobj = json.loads(buf.getvalue()) 
access_token = jsonobj['access_token']
buf.close()

def ATT_Parse(filename):
    #create a new buffer
    buf = cStringIO.StringIO()
    c.reset()

    #open the .wav file and read it in binary form
    f_open = open(filename,"rb")
    sample_file = f_open.read()

    #set the options for the pyCurl request
    c.setopt(c.URL, "https://api.att.com/rest/1/SpeechToText")
    c.setopt(c.HTTPHEADER, [("Authorization: Bearer " + access_token).encode('ascii','ignore'), "Content-Type: audio/wav", "Accept: application/json", "X-SpeechContext: BusinessSearch"])
    c.setopt(c.POSTFIELDS, sample_file) #the data file goes in the post field
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()

    result = buf.getvalue()
    jsonobj = json.loads(buf.getvalue())
    return jsonobj['Recognition']["NBest"][0]["Words"]

class Demo(Frame):
    def __init__(self,root, **options):
        Frame.__init__(self,root,**options)
        startgame = Button(self, text = "Start!", width= 10, command = self.spawnPlayRound)
        startgame.pack()

        self.resultText = Text(self,height=24,width=60)
        self.resultText.pack(side=TOP)

    def spawnPlayRound(self):
        thread.start_new(Demo.playRound, (self, ))

    def playRound(self):
        self.resultText.insert(END, "Say something!\n")
        recordaudio.record_to_file('file1.wav')
        self.resultText.insert(END, "Try and imitate the sound!\n")
        recordaudio.record_to_file('file2.wav')

        self.resultText.insert(END, "Okay processing sound 1...\n")
        result1 = ATT_Parse("file1.wav")
        self.resultText.insert(END, "AT&T thought the 1st person said: " + " ".join(result1) + "\n")
        self.resultText.insert(END, "Okay processing sound 2...\n")
        result2 = ATT_Parse("file2.wav")
        self.resultText.insert(END, "AT&T thought the 2nd person said: " + " ".join(result2) + "\n")

if __name__ == "__main__":
    root = Tk()
    root.title("Garble Flarble Game")

    uiFrame = Demo(root)
    uiFrame.pack()
    root.mainloop()
