import urllib
import re
import os
import shutil
import httplib
import urlparse

# documentation for creating docsets for Dash: http://kapeli.com/docsets/

base_url = "http://vijava.sourceforge.net/vSphereAPIDoc/ver5/ReferenceGuide/"
root_path = "vSphereAPI.docset/Contents/Resources/Documents/docs/"

token_entry_template = """<File path="docs/{}">
  <Token><TokenIdentifier>//apple_ref/cpp/{}/{}</TokenIdentifier></Token>
</File>"""

def print_index_entries(out_file, index_file, docset_type):
    """ create token entries for files linked in index_file """
    index_html = open(os.path.join(root_path, index_file), "rb").read()
    res_list = re.findall("""<a title="(.*?)(?:\s*\(in (.*?)\s*\))?" target="classFrame" href="(.*?)">(.*?)</a>""", index_html)
    for obj_name, cls_name, file_path, _ in res_list:
        if cls_name != "":
            obj_name = cls_name + "." + obj_name
        print >>out_file, token_entry_template.format(file_path, docset_type, obj_name)

def create_tokens(out_path):
    out_file = open(out_path, "wb")
    print >>out_file, '<Tokens version="1.0">'
    print_index_entries(out_file, "index-all_types.html", "cl")
    print_index_entries(out_file, "index-methods.html", "clm")
    print_index_entries(out_file, "index-properties.html", "instp")
    print_index_entries(out_file, "index-enums.html", "clconst")
    print >>out_file, "</Tokens>"

def crawl():
    conn = httplib.HTTPConnection(urlparse.urlsplit(base_url).netloc, httplib.HTTP_PORT)
    
    visited_urls = []
    urls_to_visit = ["index.html"]
    
    while len(urls_to_visit) > 0:
        cur_url = urls_to_visit.pop(0)
        local_url = os.path.join(root_path, cur_url)
        remote_url = base_url + cur_url
        print cur_url, "(%d remaining)" % len(urls_to_visit)
        if os.path.exists(local_url):
            cur_url_html = open(local_url, "rb").read()
        else:
            conn.request("GET", urlparse.urlsplit(remote_url).path)
            cur_url_html = conn.getresponse().read()
            open(local_url, "wb").write(cur_url_html)
        visited_urls.append(cur_url)
        new_urls = re.findall("(?:href|src)=['\"](?:\./)?([A-Za-z0-9-\._]+\.(?:html|js|css|png|jpg|gif))['\"]", cur_url_html, re.I)
        new_urls = [url for url in new_urls if url not in visited_urls and url not in urls_to_visit]
        new_urls = list(set(new_urls))
        urls_to_visit.extend(new_urls)

def main():
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    crawl()
    create_tokens("vSphereAPI.docset/Contents/Resources/Tokens.xml")
    shutil.copy("static/icon.png", "vSphereAPI.docset/")
    shutil.copy("static/Info.plist", "vSphereAPI.docset/Contents/")
    shutil.copy("static/Nodes.xml", "vSphereAPI.docset/Contents/Resources/")
    
    os.system("/Applications/Xcode.app/Contents/Developer/usr/bin/docsetutil index vSphereAPI.docset")
    os.system("tar --exclude='.DS_Store' -cvzf vSphereAPI.tgz vSphereAPI.docset")
    shutil.copy("static/vSphereAPI.xml", ".")

if __name__ == "__main__":
    main()