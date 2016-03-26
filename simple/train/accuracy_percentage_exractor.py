from lxml import html
import requests

def Get_Precentage():
    """
     Extract the accuracy percentage shown in the www.rail.co.il site
     Args:
         None
     Return:
         List with the percentage of accuracy
    """
    urlstr = "http://www.rail.co.il/HE/Pages/homepage.aspx"
    page = requests.get(urlstr)
    html_tree = html.fromstring(page.content)
    prct = html_tree.xpath('//span[@id="ctl00_m_g_53a07755_af4c_46c7_b31b_d8b5eea42f02_ctl00_labelPunc"]/text()')
    return prct
