from artifacts.screenshot_artifact import NewScreenshot
import pyautogui


def main():
    image = pyautogui.screenshot()
    print(image)
    image.save('temp.png')
    print(image.size)
    image_file = open('temp.png', 'rb')
    print('End of transmission. Don\'t panic!')


if __name__ == '__main__':
    main()
