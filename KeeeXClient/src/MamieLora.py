import KeeeXAPI

import argparse

def _main ():

  
    parser = argparse.ArgumentParser()
    
    
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
        KeeeXAPI.activate_http_debug()
        
    if args.proxy_host:
        KeeeXAPI.set_http_proxy_configuration (args.proxy_host, args.proxy_port)
        
    # TEST start
        
    KeeeXAPI.set_current_keeex_token ()
    
    print (KeeeXAPI._keeex_current_auth_token)
    
    return

if __name__ == '__main__':
    _main()