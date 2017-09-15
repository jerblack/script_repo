__author__ = 'Jeremy'
import pafy, pprint, os

target_dir = 'D:\\YouTube'
channel = 'Getting Doug With High'
vurl = 'https://www.youtube.com/watch?v=WaEccbF1Emc'

def getvideo():
    v = pafy.new(vurl)
    b = v.getbest()

    vid = {
        "title":        v.title,
        "channel":      channel,
        "rating":       v.rating,
        "description":  v.description,
        "published":    v.published.split(" ")[0],
        "author":       v.author,
        "resolution":   b.resolution,
        "extension":    b.extension,
        "size":         b.get_filesize(),
        "url_vid":      b.url,
        "url_page":     vurl,
        "thumbnail":    getthumb(v),
        "category":     v.category,
        "length_sec":   v.length,
        "length_hms":   v.duration,
        "username":     v.username
    }
    pprint.pprint(vid)
    # filename = b.download(callback=mycb)
    os.chdir(target_dir)
    # filename = b.download(meta=True)
    filename = "Kassem G & Nick Rutherford _ Getting Doug with High.mp4"
    df = vid['published'] + ' ' + vid['title'] + '.' + vid['extension']
    dst_fname = sanitize(df)
    print dst_fname
    # os.rename(filename, dst_fname)
    # print filename


def mycb(total, recvd, ratio, rate, eta):
    print(recvd, ratio, eta)

# cleans up string for path usage
def sanitize(str):
    keepcharacters = ' .,_-()[])'
    return "".join(c if c.isalnum() or c in keepcharacters else '-' for c in str).rstrip()

def getthumb(vt):
    if vt.bigthumbhd:
        return vt.bigthumbhd
    elif vt.bigthumb:
        return vt.bigthumb
    else:
        return vt.thumb

if __name__ == "__main__":
    getvideo()