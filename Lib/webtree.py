from selenium import webdriver
from genpath import gen_path
import re

class WebTree():
    def __init__(self, path):
        self.path = path
        self.driver = None
        self.urls = []
    
    def start(self):
        driver = webdriver.Chrome(self.path)
        options = webdriver.ChromeOptions()
        options.add_argument('--enable-javascript')
        self.driver = driver

    def store(self, url):
        self.urls.append(url)

    def run_all(self):
        for url in self.urls:
            yield self.get_clusters(url)
        
    def is_src(self, src):
        for ext in ['.jpg', '.jpeg', '.png']:
            if ext in src:
                return True
        return False
            
    def get_src(self, elem):
        src = elem.get_attribute('src')
        alt = ''
        try:
            elem.get_attribute('alt')
        except:
            print('No alt text')
            
        if not src or not self.is_src(src):
            src = elem.get_attribute('data-lazy-src')
        if not src or not self.is_src(src):
            src = elem.get_attribute('data-src')
        if self.is_src(src):
            return (src + ' ' + alt).strip()
        return ''

    

    def get_clusters(self, url):
        def build_branches(tree, curr):
            paths = []
            if isinstance(tree, str):
                idx = str(len(url_map))
                url_map[idx] = tree
                paths.append(idx)
            else:
                for key in list(tree.keys()):
                    children = build_branches(tree[key], key)
                    if children:
                        for child in children:
                            paths.append(curr.split('-')[2]+'-'+child)
            return paths
        
        clusters = []
        url_map = {}

        print('Get Clusters:', url)
        print('[ Building web tree... ]')
        tree = self.build_tree(url)

        print('[ Building branches... ]')
        paths = build_branches(tree['root-0-0'], 'root-0-0')
        paths = [path[2:] for path in paths]

        print('[ Solving paths...     ]')
        print()
        # solve paths
        while paths:
            parent_map = {}
            cluster = []
            for i in range(len(paths)):
                if '-' in paths[i]:
                    path = paths[i].split('-')
                    if path[-2] not in parent_map:
                        parent_map[path[-2]] = []
                    
                    paths[i] = '-'.join(path[:-2] + path[-1:])
                    parent_map[path[-2]].append(paths[i])
                else:
                    cluster.append(paths[i])
                    
            if cluster:
                for path in cluster:
                    paths.remove(path)

                clusters.append([url_map[path] for path in cluster])

            for key in list(parent_map.keys()):
                if len(parent_map[key]) > 1:
                    cluster = []
                    for child in parent_map[key]:
                        cluster.append(child)
                        paths.remove(child)
                        
                    clusters.append([url_map[path.split('-')[-1]] for path in cluster])
                    
        return clusters
        
    def build_tree(self, url):
        def branch(node, depth):
            tree = {}
            children = node.find_elements_by_css_selector("*")
            if children:
                for i in range(len(children)):
                    child = children[i]
                    branch_count = len(visited)
                    if child not in visited:
                        visited.append(child)
                        try:
                            if child.tag_name == 'img':
                                src = self.get_src(child)
                                if src not in visited:
                                    visited.append(src)
                                    tree['img-{}-{}-*'.format(str(depth), str(branch_count))] = src
                            else:
                                tree['{}-{}-{}'.format(children[i].tag_name, str(depth), str(branch_count))] = branch(children[i], depth+1)
                        except:
                            pass
                    
            return tree

        main_tree = {}
        visited=['root-0-0']
        self.driver.get(url)
        root = self.driver.find_element_by_css_selector('body')
        main_tree['root-0-0'] = branch(root, 1)
        
        return main_tree

    def reset(self):
        self.driver.quit()
        self.urls.clear()
