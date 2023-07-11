#preprocessing steps
import pandas as pd
from urllib.parse import urlparse
from typing import Optional, Dict
import tldextract
from nltk.tokenize import RegexpTokenizer

#extracted feature function
def extract_features(url: str) -> pd.DataFrame:
    df = pd.DataFrame({'url': [url]})
    
    #for url parsing
    def parse_url(url: str) -> Optional[Dict[str, str]]:
        try:
            no_scheme = not url.startswith('https://') and not url.startswith('http://')
            if no_scheme:
                parsed_url = urlparse(f"http://{url}")
                url_dict = {
                    "scheme": None, # not established a value for this
                    "netloc": parsed_url.netloc,
                    "domain": parsed_url.netloc.split(':')[0], # extract domain from netloc
                    "path": parsed_url.path,
                    "params": parsed_url.params,
                    "query": parsed_url.query,
                    "fragment": parsed_url.fragment,
                }
            else:
                parsed_url = urlparse(url)
                url_dict = {
                    "scheme": parsed_url.scheme,
                    "netloc": parsed_url.netloc,
                    "domain": parsed_url.netloc.split(':')[0], # extract domain from netloc
                    "path": parsed_url.path,
                    "params": parsed_url.params,
                    "query": parsed_url.query,
                    "fragment": parsed_url.fragment,
                }

            # Split path into directory and file
            directory, file = parsed_url.path.rsplit('/', 1)
            url_dict['directory'] = directory
            url_dict['file'] = file

            return url_dict
        
        except AttributeError:
            print("Invalid link: AttributeError")
            return None

        except Exception as e:
            print(f"Invalid link: {e}")
            return None
    
    # # Check if parsed_url is None
    # if df['parsed_url'].isnull().any():
    #     print("Invalid link")
    # else:
    
        # def get_length(row):
        #     return pd.Series({
        #         'url_length': len(row['url']),
        #         'domain_length': len(row['domain'])
        #     })
        
    def get_length(row):
        domain_length = len(row.get('domain', ''))
        return pd.Series({
            'url_length': len(row['url']),
            'domain_length': domain_length
            })

    #server domain
    def extract_server_client_domain(domains):
        results = []
        for domain in domains:
            parts = domain.split('.')
            if len(parts) == 3 and parts[0] == 'server':
                results.append(1)
            elif len(parts) == 2 and parts[0] != 'www':
                results.append(0)
            else:
                results.append(-1)  # invalid domain format
        return results

    def get_num_subdomains(netloc: str) -> int:
        subdomain = tldextract.extract(netloc).subdomain 
        if subdomain == "":
            return 0
        return subdomain.count('.') + 1

    #domain tokens
    tokenizer = RegexpTokenizer(r'[A-Za-z]+')
    def tokenize_domain(netloc: str) -> str:
        split_domain = tldextract.extract(netloc)
        no_tld = str(split_domain.subdomain +'.'+ split_domain.domain)
        return " ".join(map(str,tokenizer.tokenize(no_tld)))

    #applying the functions
    df['parsed_url'] = df.url.apply(parse_url) #parse urls in url_df
    df = pd.concat([
        df.drop(['parsed_url'], axis=1),
        df['parsed_url'].apply(pd.Series)], axis=1)
    
    #to get the length of characters
    length_df = df.apply(get_length, axis=1)
    df = df.merge(length_df, left_index=True, right_index=True)
    
    #tld
    df["tld"] = df.netloc.apply(lambda nl: tldextract.extract(nl).suffix)
    df['tld'] = df['tld'].replace('','None')
    
    #count symbols
    symbols = '.-'
    for char in symbols:
        df['qnty_' + char + '_url'] = df['url'].apply(lambda x: x.count(char))
        df['qnty_' + char + '_domain'] = df['domain'].apply(lambda x: x.count(char))
    
    #server domain
    df['is_server_domain'] = extract_server_client_domain(df['domain'])
    
    #num of subdomains
    df['num_subdomains'] = df['netloc'].apply(lambda net: get_num_subdomains(net))
    
    #domain tokens
    df['domain_tokens'] = df['netloc'].apply(lambda net: tokenize_domain(net))
    
    #tokens
    tok= RegexpTokenizer(r'[A-Za-z0-9]+')
    df['tokenized_url'] = df['url'].map(lambda x: tok.tokenize(x))
    
    #drop unecessary columns
    cols_to_drop = ['netloc', 'domain', 'path', 'params', 'query', 'scheme',
            'fragment', 'directory', 'file']
    df.drop(cols_to_drop, axis=1, inplace=True)
        
    return df


#exceptions:
# url = extract_features("http://americantowergroup.in") #phish
# url = extract_features("https://github.com") #legit
# # print(url)