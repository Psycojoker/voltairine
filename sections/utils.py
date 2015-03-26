def unfold_tree(tree):
    def get_childrens(node):
        childrens = []
        for i in node[1]:
            childrens.append(i[0])
            childrens.extend(get_childrens(i))
        return childrens

    def _recurse(subtree):
        for i in subtree:
            result[i[0]] = get_childrens(i)
            _recurse(i[1])


    result = {}
    _recurse(tree)

    return result
