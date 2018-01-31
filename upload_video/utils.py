import os
import string
import random

from django.template.defaultfilters import slugify


def generate_random_string(size):
    return ''.join(random.SystemRandom().choice(string.hexdigits) for n in xrange(size))



def clean_file_name(file_name):
    if "." in file_name:
        file_name = slugify(".".join(file_name.split(".")[:-1])) + "." + file_name.split(".")[-1]
    else:  # strange, no extension situation
        file_name = slugify(file_name)

    return file_name


def ensure_file_name_is_unique(destination, file_name):
    # not the best strategy, but good enough
    # shouldn't loop more than 1 time, maybe 2-3 in the worst situation
    while os.path.exists(os.path.join(destination, file_name)):
        file_name = file_name.split(".")
        assert len(file_name) > 0
        if len(file_name) > 1:
            file_name.insert(-1, generate_random_string(10))
            file_name = ".".join(file_name)
        else:
            file_name = "%s_%s" % (file_name[0], generate_random_string(10))

    return file_name
