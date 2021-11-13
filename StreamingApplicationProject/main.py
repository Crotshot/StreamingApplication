import Stream
streamScript = Stream


def inputOption(text, successList):
    choice = input(text)
    if choice in successList:
        return True
    else:
        return False


def inputs():
    # if inputOption("Are you joining or hosting a stream (j/h)? ", ['h', 'H']):
    #     streamScript.source = True
    #     if inputOption("Would you like to stream your webcam or screen (w/s)? ", ['w', 'W']):
    #         choice = input("Which webcam would you like to use (0 for primary, 1 for secondary etc etc)? ")
    #         streamScript.webcamNumber = int(choice)
    #         streamScript.sourceInput = "Webcam"
    #         print("Showing Webcam " + str(streamScript.webcamNumber))
    #     else:
    #         streamScript.sourceInput = "Screen"
    #         print("Showing screen")
    # else:
    #     streamScript.source = False

    #############################################
    #Remove after testing
    streamScript.source = True
    streamScript.sourceInput = "Screen"
    #############################################

if __name__ == '__main__':
    inputs()
    streamScript.app.run(host='0.0.0.0', port=5000, debug=False)