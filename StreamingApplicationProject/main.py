from waitress import serve
import Stream
import socket
import webbrowser
ipAddress = socket.gethostbyname(socket.gethostname())

if __name__ == '__main__':
    #webbrowser.open_new("http://" + ipAddress + ":8080/")
    serve(Stream.app, host='127.0.0.1', port=8080)

    # streamScript.sourceInput = "Screen"
    # streamScript.app.run(host='0.0.0.0', port=5000, debug=False)#, threaded=True, processes=1)

    #OLD

    # def inputOption(text, successList):
    #     choice = input(text)
    #     if choice in successList:
    #         return True
    #     else:
    #         return False

    # def inputs():
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
    # Remove after testing

    #############################################