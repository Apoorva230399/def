import os
import re
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import openai

def extract_classes_functions(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # print(content)

    class_name = None
    functions = []

    class_match = re.search(r'\bpublic\s+(?:with sharing\s+)?class\s+(\w+)\s*{', content)
    if class_match:
        class_name = class_match.group(1)

    function_matches = re.findall(r'\bpublic\s+static\s+\w+\s+(\w+)\s*\(', content)
    functions.extend(function_matches)

    return class_name, functions

def find_dependencies(file_path, all_classes):
    with open(file_path, 'r') as f:
        content = f.read()
        
    dependencies = {}
    
    for class_name in all_classes:
        if class_name in content:
            function_calls = re.findall(rf'{class_name}\.(\w+)\s*\(', content)
            if function_calls:
                dependencies[class_name] = function_calls
    # print(dependencies)
    return dependencies

import matplotlib.pyplot as plt
import networkx as nx
import os

#ASSUMPTION: Assume extract_classes_functions and find_dependencies functions are defined

def main(folder_path):
    fig = plt.figure(figsize=(12, 8))

    ax1 = fig.add_axes([0.1, 0.1, 0.6, 0.8])
    plt.sca(ax1)

    class_files = [f for f in os.listdir(folder_path) if f.endswith('.cls')]

    class_function_map = {}
    for class_file in class_files:
        class_name, functions = extract_classes_functions(os.path.join(folder_path, class_file))
        if class_name:
            class_function_map[class_name] = functions
    # print(class_function_map)
    G = nx.DiGraph()
    content_list = ""
    for class_file in class_files:
        class_name, _ = extract_classes_functions(os.path.join(folder_path, class_file))
        if not class_name:
            continue
        G.add_node(class_name, type='class')

        dependencies = find_dependencies(os.path.join(folder_path, class_file), class_function_map.keys())

        
        for dep_class, dep_methods in dependencies.items():
            G.add_edge(class_name, dep_class)
            for dep_method in dep_methods:
                G.add_node(f"{dep_class}.{dep_method}", type='method')
                G.add_edge(dep_class, f"{dep_class}.{dep_method}")
                G.add_edge(class_name, f"{dep_class}.{dep_method}")
                # print(f"{class_name} depends on {dep_class} via method {dep_method}")
                content = f"{class_name} depends on {dep_class} via method {dep_method}"
                # content_list.append(content)  # Append the content to the list
                content_list += content+"\n"

    
    # print(content_list)

    # Split the text into lines and extract dependency information
    lines = content_list.split('\n')
    dependencies = []

    for line in lines:
        parts = line.split(' depends on ')
        if len(parts) == 2:
            dependent, dependency_info = parts
            dependency_parts = dependency_info.split(' via method ')
            if len(dependency_parts) == 2:
                dependency, method = dependency_parts
                dependencies.append((dependent, dependency, method))

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph based on the dependency information
    for dep in dependencies:
        G.add_edge(dep[0], dep[1], method=dep[2])

    # Find independent nodes
    independent_nodes = [node for node in G.nodes() if G.out_degree(node) == 0]

    # Find dependent nodes
    dependent_nodes = [node for node in G.nodes() if G.out_degree(node) > 0]

    # Print the results
    # print("Independent Nodes:", independent_nodes)
    # print("Dependent Nodes:", dependent_nodes)
    # print(content_list)

    # Split the input string by lines and filter out empty lines
    lines = [line for line in content_list.split('\n') if line.strip()]

    # Dictionary to store dependencies
    dependency_dict = {}

    # Iterate over each line and extract the relevant classes
    for line in lines:
        try:
            parts = line.split(" depends on ")
            source = parts[0].strip()  # Added strip() to handle potential leading/trailing spaces
            destination = parts[1].split(" via ")[0].strip()  # Same here

            # Update dictionary with the new dependency
            if source in dependency_dict:
                if destination not in dependency_dict[source]:
                    dependency_dict[source].append(destination)
            else:
                dependency_dict[source] = [destination]

        except IndexError:
            # Handle any lines that don't fit the expected format gracefully
            pass

    # Convert lists to single strings for entries with only one dependency
    # for key, value in dependency_dict.items():
    #     if len(value) == 1:
    #         dependency_dict[key] = value[0]

    # print(dependency_dict)

    ##sort in required order
    # Sorting function that handles both string and list values
    def custom_sort(item):
        value = item[1]
        if isinstance(value, list):
            # Convert list to a concatenated string for comparison
            return ''.join(sorted(value))
        return value

    # Sort the dictionary by its values
    sorted_data = dict(sorted(dependency_dict.items(), key=custom_sort))

    # print(sorted_data)

    data_dict = sorted_data

    # Variable with list of keys to check
    # keys_to_check = ['manager']
    keys_to_check = independent_nodes

    for key in keys_to_check:
        if key not in data_dict:
            # Insert the key-value pair at the start of the dictionary
            data_dict = {key: [], **data_dict}

    # print(data_dict)

    # directory_path = r"C:\Users\asrinivas\Documents\larcas\Input_files"
    directory_path = folder_path

    # Initialize an empty dictionary to store file content
    file_contents = {}

    # List all .cls files in the directory
    cls_files = [file for file in os.listdir(directory_path) if file.endswith(".cls")]

    # Read the content of each .cls file and store it in the dictionary
    for file_name in cls_files:
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()
            
            # Get the filename without extension
            name_without_extension = os.path.splitext(file_name)[0]
            
            # Add the content to the dictionary with the filename (without extension) as the key
            file_contents[name_without_extension] = file_content

    # Print the dictionary
    # print(file_contents)



    # Flatten the values, filter out 'null' and also include the keys
    # unique_values = set(value for key, values in data_dict.items() for value in (values if isinstance(values, list) else [values]) if value != 'null').union(data_dict.keys())

    # print(unique_values)

    def get_userstory_by_code(code,method_desc) :
        # Set your OpenAI API key
        api_key = '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'
        prompt_0 = '''You are an user story expert.You convert given any code to it's functional user story.\n
        while coneverting rules to follow:\n
        ---------------------\n
        1.Don't mention any method names or technical detailing.\n
        -------------------------\n
        Below is the code snippet:\n
        --------------\n
        {code}
        --------------\n
        Find some sub methods summary for reference dict (method_name:method desc):\n
        --------------\n
        {method_desc}
        --------------\n
        Generated userstory:
        '''
        prompt = prompt_0.format(code=code,method_desc = method_desc)

        # Call the OpenAI API to generate a response
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the appropriate engine
            prompt=prompt,
            max_tokens=811,  # You can adjust the max_tokens parameter as needed
            api_key=api_key,
            temperature = 0,
        )

        # Extract the generated text from the response
        generated_text = response.choices[0].text

        # Print the generated text
        out = generated_text.strip()
        return out
    
    def final_ans(data_dict):
        method_desc_dict = {}
        # Iterate over the classes
        for key, value in data_dict.items():
            source_code = file_contents[key]
            sub_method_desc_dict = {}
            if method_desc_dict != {} :
                # print(value)
                sub_method_desc_dict = {key: method_desc_dict[key] for key in value}
                # print(sub_method_desc_dict)              
            code_desc = get_userstory_by_code(source_code,sub_method_desc_dict)
            method_desc_dict[key] = code_desc
        return method_desc_dict
    # print(data_dict)
    # print(final_ans(data_dict))
    output = final_ans(data_dict)
    # print(output)
    for key, value in output.items():
        print(f'method :{key},method_desc:{value}')
        print('\n')


    # shell_pos = []
    # all_classes = [n for n, attr in G.nodes(data=True) if attr['type'] == 'class']
    # all_methods = [n for n, attr in G.nodes(data=True) if attr['type'] == 'method']

    # shell_pos.append(all_methods)
    # shell_pos.append(all_classes)

    # # print(shell_pos)

    # pos = nx.shell_layout(G, shell_pos)
    # # print(pos)
    # nx.draw(G, pos, with_labels=False, node_color='lightblue', font_weight='bold', node_size=700)

    # label_mapping = {}
    # for i, node in enumerate(G.nodes):
    #     label_mapping[node] = i + 1
    #     x, y = pos[node]
    #     plt.text(x, y, str(i + 1), fontsize=12, ha='center', va='center')

    # ax1.axis('off')

    # ax2 = fig.add_axes([0.75, 0.1, 0.2, 0.8])
    # ax2.axis('off')

    # plt.text(0.0, 1.0, '\n'.join(f"{i+1}: {node}" for i, node in enumerate(G.nodes)),
    #          fontsize=12, ha='left', va='top', transform=ax2.transAxes)

    # plt.savefig('plot.png')

    # plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate Salesforce dependency graph.')
    parser.add_argument('folder_path', type=str, help='Path to folder containing .cls files')
    
    args = parser.parse_args()
    main(args.folder_path)

