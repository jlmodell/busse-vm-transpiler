import imaplib
import email
from email.header import decode_header
import re
import asyncio
import speech_recognition as sr
from pydub import AudioSegment
import io

transcribed_msgs = {}


async def email_checker_for_voicemails_hook(id: str = "Voicemail"):
    global transcribed_msgs

    with imaplib.IMAP4_SSL(host="imap.siteprotect.com", port="993") as m:
        m.login("gcoreas@busseinc.com", "GLdirea1#")
        _, messages = m.select()

        n = 10
        messages = int(messages[0])

        for i in range(messages, messages - n, -1):
            _, msg = m.fetch(str(i), "(RFC822)")            
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    
                    if isinstance(subject, bytes):
                        try:
                            subject = subject.decode("utf-8")
                        except UnicodeDecodeError:
                            subject = subject.decode("cp1252")
                        
                        except:
                            continue                    

                    if re.search(rf"^{id}", subject):                        
                        for part in msg.walk():                            
                            if part.get_content_maintype() == "audio":
                                filename = part.get_filename()
                                if filename and ".mp3" in filename and filename not in transcribed_msgs:
                                    r = sr.Recognizer()
                                    audiobytes = io.BytesIO(part.get_payload(decode=True))
                                    wav = AudioSegment.from_file(audiobytes, "mp3").export(format="wav")
                                    with sr.AudioFile(wav) as source:
                                        audio = r.record(source)
                                                                    
                                    transcribed_msgs[filename] = r.recognize_google(audio)

        return transcribed_msgs
                           



if __name__ == "__main__":
    asyncio.run(email_checker_for_voicemails_hook())
