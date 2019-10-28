# $Id$

import string

import json
import base64
import datetime

import urllib.parse
import urllib.request
import ssl

import http.client

import logging

import argparse

_defaults = {
    'contentTypeList' : ['document', 'post', 'discussion', 'event'],
    'jiveUser': "XXXXXXXXXXXXXXXXXXXX", #User must have admin permissions
    'jivePassword' : "YYYYYYYYYYYYYYY",
    'jiveServerBaseUrl' : "https://plazza.orange.com",
    'classification_print_template' : '<h1>$digest_classification_tag</h1>'
}


#Variables
_jive_date_strftime_formater = '%Y-%m-%dT00:00:00Z'
_classifier_printing_string_template = None
_debug = False

_keeex_api_port = 8288
_keeex_api_host = 'localhost'

#_keeex_api_port = 8288
#!!!_keeex_api_host = '10.193.224.199'

_keeex_api_base_url = 'http://%s:%d/kx/api' % (_keeex_api_host, _keeex_api_port)
_keeex_token_url = _keeex_api_base_url + '/token'

_keeex_current_auth_token = None

_urllib_proxy_specification = {}

def set_current_keeex_token (application_name = 'my python client'):
    
    url = _keeex_token_url
    headers = {}
    
    headers["Content-Type"] = "application/json"
    
    json_body_arg = {
        "appName" : application_name
    }
    
    json_str = json.dumps (json_body_arg)
    
    request_body = json_str.encode(encoding='utf_8')
    
    try:
        
        if _debug:
            http_debug_level_flag = 1
        else:
            http_debug_level_flag = 0
        
        http_handler = urllib.request.HTTPHandler(debuglevel=http_debug_level_flag)
        
        proxy_handler = urllib.request.ProxyHandler (_urllib_proxy_specification)
        
        opener = urllib.request.build_opener(http_handler, proxy_handler)

        # install it
        urllib.request.install_opener(opener)
        
        req = urllib.request.Request(url=url, headers=headers, data=request_body, method='GET')

        response = urllib.request.urlopen(req, timeout=10)
        b_data = response.read()
        response_data = b_data.decode('utf-8')
        
        print (response_data)
        
        #Load json with request text
        jsonData = json.loads(response_data)
        
        if  'token' in jsonData:
            _keeex_current_auth_token = jsonData["token"]

    except urllib.error.HTTPError as e:
        print (e)
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
  
    except urllib.error.URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)

    
    


def content_type_to_jive_uri (content_type, content_id):
    
    content_type_to_uri_format = {
        'document': '/docs/DOC-%s',
        'discussion': '/thread/%s',
        'event' : '/events/%s'
    }    
    
    uri_to_content_formater = content_type_to_uri_format.get(content_type, '/%s')
    content_uri = uri_to_content_formater % content_id 
    
    return content_uri
    

def get_jive_date_interval (year, weeknumber, day_range = 7):
    
    first_year_day = datetime.datetime (year = year, month = 1, day = 1)
    weekday_of_first_year_day = first_year_day.weekday() # monday == 0, synday = 7
    week01_start_date = first_year_day - datetime.timedelta (weekday_of_first_year_day)
    
    days_to_week_number_first_day = (weeknumber - 1) * 7
    week_number_beginning_date = week01_start_date + datetime.timedelta (days = days_to_week_number_first_day)
    week_number_end_date = week_number_beginning_date + datetime.timedelta (days = day_range)
    
    #yyyy-MM-dd'T'HH:mm:ss.SSSZ
    
    jive_date_week_number_beginning_date = week_number_beginning_date.strftime (_jive_date_strftime_formater)
    jive_date_week_number_end_date = week_number_end_date.strftime (_jive_date_strftime_formater)
    
    return (jive_date_week_number_beginning_date, jive_date_week_number_end_date)

def jive_html_ref_for_document (dataItem, short_display = True):

    subject = dataItem["subject"]
    content_text = dataItem["content"]["text"]
    id = dataItem["id"]
    type = dataItem["type"]    
    published = dataItem["published"]
    author_id = dataItem["author"]["id"]
    author_displayName = dataItem["author"]["displayName"]
    author_jive_username = dataItem["author"]["jive"]["username"]
    lastActivity = dataItem["lastActivity"]

    
    content_text_body_content = content_text[6:-7]
  
    uri_to_content = content_type_to_jive_uri (type, id)
    
    if short_display:
        # short format: only title & author display
        print ('<p/>')
        print ('<p>')
        print ('<a href="%s">%s</a> ' % (uri_to_content, subject))
        print ('</p>')
        print ('<p>')  
        print ('Author: <a href="/people/%s">%s</a>' % (urllib.parse.quote(author_jive_username), author_displayName))
        print ('</p>')                          
       
    else:
        # long format: includes body
        print ('<hr>')
        print ('<hr>')   
        print ('<h2>%s</h2>' % subject) 
        print ('<p>')
        print ('Report: <a href="%s">%s</a> ' % (uri_to_content, subject))
        print ('By: <a href="/people/%s">%s</a>' % (urllib.parse.quote(author_jive_username), author_displayName))
        print ('</p>')
        print ('<hr>')       
    
        print ('<p>')        
        print (content_text_body_content)
        print ('</p>')        
             
    
def get_list_of_document_list (document_types, tags, credential, start = 0, maxReturn = 100, date_range = None):
    global _debug
    
    headers = {}
    # FIXME: credential should be managed by Basic Auth Handler
    user, password = credential
    
    credatial_string = '%s:%s' % (user, password)
    utf8_credatial_string = credatial_string.encode('utf-8')    
    
    zzz1 = base64.encodebytes(utf8_credatial_string)
    tt = zzz1.decode('utf-8').replace("\n","")

    auth = "Basic " + tt
    headers['Authorization'] = auth
    
    headers["Accept"] = "*/*"
    headers["Content-Type"] = "application/json"
    

    base_url = _defaults['jiveServerBaseUrl']
    
    remainingContent = True
    
    filtering_arg_list = []
    
    type_filter_arg = ','.join (document_types)
    filtering_arg_list += [ 'filter=type(%s)' % type_filter_arg ]
    #Group invites uri
    
   
    # tag list filtering
    tag_filter_arg = ' AND '.join (tags)
    quoted_tag_filter_arg = urllib.parse.quote (tag_filter_arg)
    filtering_arg_list += [ 'filter=tag(%s)' % quoted_tag_filter_arg ]
    
    # date range filtering
    if date_range:
        year, week_number = date_range
        start_date, end_date = get_jive_date_interval (year, week_number)
        filtering_arg_list += [ 'filter=modificationDate(%s,%s)' % (end_date, start_date) ]
        
    retrieved_data_list = [] 
    
    #Loop through and compile all invites
    while (remainingContent):
        
        single_call_filtering_arg_list = filtering_arg_list
        
        # paging argument
        count_filter_arg = 'count=%s' % maxReturn
        single_call_filtering_arg_list += [ count_filter_arg ]
        
        startIndex_filter_arg = 'startIndex=%s' % start
        single_call_filtering_arg_list += [ startIndex_filter_arg ]        
        
        # create the url argument string
        url_argument_string = '&'.join(single_call_filtering_arg_list)

        uri = '/api/core/v3/contents?%s' % url_argument_string
        
        url = base_url + uri
        start += maxReturn
    
        try:
            
            if _debug:
                http_debug_level_flag = 1
            else:
                http_debug_level_flag = 0
            
            http_handler = urllib.request.HTTPHandler(debuglevel=http_debug_level_flag)
            
            # needed with SSL "man in the middle" proxification (to debug the traffic)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE                        
            https_handler = urllib.request.HTTPSHandler(debuglevel=http_debug_level_flag, context=ctx)

            passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            user, password = credential
            passman.add_password(None, url, user, password)
            authinfo_handler = urllib.request.HTTPBasicAuthHandler(passman)
            
            proxy_handler = urllib.request.HTTPBasicAuthHandler ({'http': 'http://localhost:8888/', 'https': 'http://localhost:8888/'})

            opener = urllib.request.build_opener(authinfo_handler, http_handler, https_handler, proxy_handler)

            # install it
            urllib.request.install_opener(opener)
            
            req = urllib.request.Request(url=url, headers=headers)

            response = urllib.request.urlopen(req, timeout=20)
            b_data = response.read()
            data = b_data.decode('utf-8')
    
        except urllib.error.HTTPError as e:
            print (e)
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            # return an empty list
            return []            
        except urllib.error.URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            # return an empty list
            return []
        
        #Remove security header
        data2 = data.replace("throw 'allowIllegalResourceCall is false.';", "")
        
        #Load json with request text
        jsonData = json.loads(data2)
        #print jsonData

        jsonDataList = jsonData["list"]
        if len(jsonDataList) < maxReturn:
            # return less that requested => got all the content
            remainingContent = False
        else:
            start += maxReturn
            
        retrieved_data_list += [ data2 ]
            
        return retrieved_data_list
            

def html_print_of_retrieved_data_list (retrieved_json_content_list, content_type_list, tag_list, digest_year, digest_week_number, classification_tags = None, classification_labels = None, short_display = True):
    
    global _classifier_printing_string_template
    
  
    print ('''
<!-- Digest
   content of type: %s
   filtered by tags (and filter): %s
   for week number %s of year %s
-->''' % (','.join(content_type_list), ','.join(tag_list), digest_week_number, digest_year))
    
    print ('''
<body>
''')
    
    if not short_display:
        print ('''
<h1><img class="jive_macro jive_macro_toc" src="/8.0.3.6eafe9c/images/tiny_mce3/plugins/jiveemoticons/images/spacer.gif" jivemacro="toc" /></h1>
''')     
    
    # initialize classified data items table
    classified_dataItems = dict ()
    for classification_tag in classification_tags:
        classified_dataItems[classification_tag] = []
        
    
    # classification of content
    for list_item in retrieved_json_content_list:
        jsonData = json.loads(list_item)
        jiveContentJsonList = jsonData["list"]
        for dataItem in jiveContentJsonList:
            dataItem_tags = dataItem["tags"]
            has_been_classified = False
            for classification_tag in classification_tags:
                if classification_tag in dataItem_tags:
                    classified_dataItems[classification_tag].append(dataItem)
                    has_been_classified = True
            if not has_been_classified:
                classified_dataItems["__unclassified__"].append(dataItem)
                  
    for classification_tag in classification_tags:        
        # get the printable classification label
        if classification_tag in classification_labels:
            classification_string = classification_labels[classification_tag]
        else:
            classification_string = classification_tag

        user_formated_classification_string = _classifier_printing_string_template.substitute(digest_classification_tag=classification_string)
        print (user_formated_classification_string)
        for dataItem in classified_dataItems[classification_tag]:
            jive_html_ref_for_document (dataItem, short_display = short_display)
            
          
    print ('''
</body>
''')    
        
def _check_week_number_arg (parser, week_number_string):
    
    try:
        week_number = int(week_number_string)
    except ValueError:
        parser.error("week number (%s) is not an integer" % week_number_string)  
    
    if (week_number < 1) or (week_number > 52):
        parser.error("week number (%s) should be in a valid range (1-52)" % week_number)
        
    return week_number

def activate_http_debug ():
    global _debug
    
    _debug = True
    
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1
    
def get_classification_label_specification_from_args (classification_and_label_tag_list):
    
    classification_tag_list = []
    classification_labels = {}
    
    for classification_and_label_tag_specification in classification_and_label_tag_list:
        equal_char_occurence_index = classification_and_label_tag_specification.find('=')
        if equal_char_occurence_index != -1:
            # specification is of the form <classification_tag=classification_label>
            classification_tag=classification_and_label_tag_specification[:equal_char_occurence_index]
            classification_label=classification_and_label_tag_specification[equal_char_occurence_index+1:]
            
        else:
            classification_tag=classification_and_label_tag_specification
            classification_label=None
            
        if (len(classification_tag) == 0):
            # ignore this specification
            continue
                            
        # add the tag to tag list if not already in list
        if not classification_tag in classification_tag_list:
            classification_tag_list.append (classification_tag)
            
        # create/overide classification label if specified, even if it is an empty string
        if classification_label:
            classification_labels[classification_tag] = classification_label
        
    # if __unclassified__ do not occur, force existence
    if not '__unclassified__' in classification_tag_list:
        classification_tag_list.append ('__unclassified__')    
    
    result = (classification_tag_list, classification_labels)
    
    return result
    

def _main ():
    
    global _urllib_proxy_specification
    global _classifier_printing_string_template

    
    parser = argparse.ArgumentParser()
    
    current_year = datetime.date.today().year
    
#     parser.add_argument("--year", type=int, action="store", help="year to consider for digest (YYYY). Defaults to current year", default=current_year)
#     parser.add_argument("--week_number", type=lambda x: _check_week_number_arg(parser, x), required=True, help="iso week number to digest")
#     parser.add_argument("--content", choices=['document', 'discussion', 'post', 'update'], help="type of content to retreive", default=_defaults['contentTypeList'])
#     parser.add_argument("--user", help="username to use to connect to Plazza", default=_defaults['jiveUser']) 
#     parser.add_argument("--password", help="user password to use to connect to Plazza", default=_defaults['jivePassword']) 
#     parser.add_argument("--tag", dest='tag_list', action='append', help="tag for content filtering", default=[])
#     parser.add_argument("--url_quoted_tag", dest='url_quoted_tag_list', action='append', help="same as --tag, but passed as url quoted string", default=[])
#     parser.add_argument("--digest_classification_tag", dest='digest_classification_tag_specification_list', action='append', help="tag for content display classification (<=label> suffix display the <label> in classification)", default=[])
#     parser.add_argument("--digest_classification_url_quoted_tag", dest='digest_classification_url_quoted_tag_specification_list', action='append', help="same as --digest_classification_tag, but passed as url quoted string", default=[])
#     parser.add_argument("--classification_print_template", type=str, action="store", help="pattern to use for printing classifier. Defaults to %s" % _classifier_printing_string_template, default=_defaults['classification_print_template'])
#     parser.add_argument("--with_content_body", action="store_true", help='tell to print also the body of the retrieved content')
    parser.add_argument("--proxy_host", type=str, help='proxy hostname if a HTTP proxy has to be used')
    parser.add_argument("--proxy_port", type=int, help='proxy port number associated with --proxy_host is specified')    
    parser.add_argument("--debug", action='store_true')     
  
    args = parser.parse_args()
    
    if args.debug:
        activate_http_debug()
        
    if args.proxy_host:
        if args.proxy_port:
            proxy_url = 'http://%s:%d/' % (args.proxy_host, args.proxy_port)
        else:
            proxy_url = 'http://%s:8080/' % args.proxy_host
        
        _urllib_proxy_specification = {'http': proxy_url, 'https': proxy_url } 
        
    # TEST start
        
    set_current_keeex_token ()
    
    print (_keeex_current_auth_token)
    
    return
    #################################################
        
    display_short = True
    if args.with_content_body:
        display_short = False
 
    # unquote search-tag params
    dequoted_tag_list = list (map (urllib.parse.unquote, args.url_quoted_tag_list))
    all_tag_list = args.tag_list + dequoted_tag_list
    
    # unquote classification-tag params
    dequoted_digest_classification_tag_specification_list = list (map (urllib.parse.unquote, args.digest_classification_url_quoted_tag_specification_list))
    all_digest_classification_tag_specification_list = args.digest_classification_tag_specification_list + dequoted_digest_classification_tag_specification_list
    
    digest_classification_tag_list, digest_classification_labels = get_classification_label_specification_from_args (all_digest_classification_tag_specification_list)
    
    # overide global params
    _classifier_printing_string_template = string.Template (args.classification_print_template)
    
    # all args validated
    retrieved_data_list = get_list_of_document_list(args.content, all_tag_list, date_range = (args.year, args.week_number), credential = (args.user, args.password))
    html_print_of_retrieved_data_list (retrieved_data_list, args.content, all_tag_list, args.year, args.week_number, digest_classification_tag_list, digest_classification_labels, display_short)

if __name__ == '__main__':
    
    _main ()
    
