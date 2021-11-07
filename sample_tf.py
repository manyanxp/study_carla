import tensorflow as tf


def main():
    print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))


if __name__ == '__main__':
    main()
