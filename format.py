import os
from pathlib import Path
def reformat_data(path):
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            cols = line.split("|")

            wav_path = "/kaggle/input/ngochuyen-24k-rvc/ngochuyen_RVC_24k/" + cols[0] + ".wav"
            old_text = cols[1].replace("~", "##")

            text, tone = text_to_text(old_text)
            text = text[1:]
            tone = tone[1:]
            new_item = wav_path + "|" + text + "|" + tone + "|" + str(0) + "\n"
            with open("metadata_ngochuyen.txt", "a") as f:
                f.write(new_item)

def text_to_text(text):
    new_text = ""
    new_tone = ""

    multi_syls = []
    multi_tones = []
    words = text.split()
    for word in words:
        if word == "#" or word == "##":
            new_text += word + " " 
            new_tone += "$"*len(word) + " "
        elif "-" in word:
            syls = word.split("-")
            for syl in syls:
                if len(syl) == 1:
                    multi_syls.append(syl)
                    multi_tones.append("1")
                else:
                    multi_syls.append(syl[:-1])
                    multi_tones.append(syl[-1]*len(syl[:-1]))

            new_text += "-".join(multi_syls) + " "
            new_tone += "$".join(multi_tones) + " "
        else:
            new_text += word[:-1] + " "
            new_tone += word[-1]*len(word[:-1]) + " "
    # print(new_text)
    # print(new_tone)
    return new_text, new_tone

# text_to_text("# tak6-zuNm7 tsi3 # 9Xw3 # k9Xm2 maXw5 #")
if __name__ == "__main__":
    reformat_data(Path(r"C:\StyleTTS-test\ngochuyen_text_char2.txt"))