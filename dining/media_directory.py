def image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dining/image/{0}/{1}'.format(instance.id, filename)

def representative_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dining/representative/{0}/{1}'.format(instance.id, filename)

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'menu/{0}/{1}'.format(instance.restaurant.id, filename)

def food_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dining/food/{0}/{1}'.format(instance.restaurant.id, filename)

def restaurant_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dining/restaurant/{0}/{1}'.format(instance.restaurant.id, filename)

def menu_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dining/menu/{0}/{1}'.format(instance.restaurant.id, filename)