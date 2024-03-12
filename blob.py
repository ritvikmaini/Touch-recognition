import time
import cv2
import numpy as np
from touch import Touch, delete_duplicates
from pythontuio import TuioServer, Cursor
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
import pygame

def fingerDown(cursor_id, x, y, server):
    normalized_x, normalized_y = normalize(x, y)
    cursor = Cursor(cursor_id)
    cursor.position = (normalized_x, normalized_y)
    server.cursors.append(cursor)
    return server
def fingerMoved(cursor_id, x, y, server):
    normalized_x, normalized_y = normalize(x, y)
    cursor = next((c for c in server.cursors if c.session_id == cursor_id), None)
    if cursor:
        cursor.position=(normalized_x, normalized_y)
    # server.send_bundle()
    return server
def fingerUp(cursor_id, server):
    if cursor_id in server.cursors:
        server.cursors.remove(cursor_id)
        print(f"REMOVE: Cursor ID: {cursor_id}")
    #server.send_bundle()
    return server
def normalize(x, y):
    return (x / width), (y / height)
def tuiodemo_simulation_matplotlib(touch_points_queue):
    #plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()

    while True:
        touch_points = touch_points_queue.get()
        if touch_points == "STOP":
            break

        ax.clear()
        ax.set_xlim(0, 1)  # Normalized coordinates
        ax.set_ylim(0, 1)  # Normalized coordinates

        for touch in touch_points:
            ax.scatter(*touch, color='blue')

        plt.draw()
        plt.pause(0.1)

    plt.ioff()
    plt.close()
    return plt
def show(current, frame, current_frame, ms_time, previous, server):

    for touch_instance2 in current:
        base_x = int(touch_instance2.get_x()) + 5
        base_y = int(touch_instance2.get_y()) - 5

        # Display ID
        cv2.putText(frame, "ID:" + str(touch_instance2.get_id()),
                    (base_x, base_y),
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 0), 1, 8)

        # Display X value
        cv2.putText(frame, "X:" + str(int(touch_instance2.get_x())),
                    (base_x, base_y + 10),  # Adjust y-coordinate
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 80, 80), 1, 8)

        # Display Y value
        cv2.putText(frame, "Y:" + str(int(touch_instance2.get_y())),
                    (base_x, base_y + 20),  # Adjust y-coordinate
                    cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 80, 80), 1, 8)

        nearest_touch = touch_instance2.nearest(current)
        if nearest_touch.get_id() > 0:
            # Draw a line between touch_instance2 and its nearest neighbor
            cv2.line(frame, (int(touch_instance2.get_x()), int(touch_instance2.get_y())),
                     (int(nearest_touch.get_x()), int(nearest_touch.get_y())), (200, 200, 200), 1)
            # Calculate the distance between touch_instance2 and its nearest neighbor
            distance = touch_instance2.calc_distance(nearest_touch)
            # Display the distance near the midpoint of theq line
            midpoint = ((int(touch_instance2.get_x()) + int(nearest_touch.get_x())) // 2,
                        (int(touch_instance2.get_y()) + int(nearest_touch.get_y())) // 2)

            cv2.putText(frame, "{:.2f}".format(distance), midpoint, cv2.FONT_HERSHEY_PLAIN,
                        0.8, (200, 200, 200), 1, 8)

    cv2.putText(frame, "frame #" + str(current_frame), (0, 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 4)
    cv2.putText(frame, "time per frame: " + str(ms_time * 1000) + "ms", (0, 30), cv2.FONT_HERSHEY_PLAIN, 1,
                (255, 255, 255), 1, 1)
    cv2.imshow("Result Window", frame)
def filters(frame, idCounter, current, previous):
    dframe = cv2.absdiff(frame, original)
    blurred = cv2.blur(dframe, (20, 20))
    highpass = cv2.absdiff(dframe, blurred)
    _, binarized = cv2.threshold(highpass, 10, 255, cv2.THRESH_BINARY)
    cv2.imshow("binarised", binarized)
    # show_contours=np.zeros((binarized.shape[0],binarized.shape[1]),dtype=np.uint8)
    contours, hierarchy = cv2.findContours(binarized, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours, hierarchy
def existence(obj, previous):
    condition = False
    for touch in previous:
        if obj.get_id() == touch.get_id():
            condition = True
    return condition
# Adding New Touch Points
def visualise_touch_events(current,server):  # tuiodemo
    pygame.init()
    font = pygame.font.SysFont(None, 20)
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("DEMO")

    while True:
        '''for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return'''
        screen.fill((80, 80, 80))
        for cursor in server.cursors:
            for touch in current:
                if cursor.session_id == touch.get_id():
                    normx,normy=normalize(touch.get_x(),touch.get_y())
                    pygame.draw.circle(screen, (200,200,200), (int(normx * 800), int(normy * 600)), 10,2)
                    text = font.render(f"ID: {int(touch.get_id())}", True,(0, 0, 0))
                    text2 = font.render(f"(X: {int(touch.get_x())},",
                                       True,
                                       (200, 200, 200))
                    text3 = font.render(f"Y: {int(touch.get_y())})", True,(200, 200, 200))
                    # 3. Blit (draw) the rendered text onto the screen.
                    screen.blit(text, (int(normx * 800), int(normy * 600) +20))
                    screen.blit(text2, (int(normx * 800), int(normy * 600) +40))
                    screen.blit(text3, (int(normx * 800), int(normy * 600) +60))

        pygame.display.flip()
        return screen
def print_touch_events(current,server):  # tuiodump
    for cursor in server.cursors:
        for touch in current:
                if cursor.session_id == touch.get_id():
                    print(f"Cursor ID: {touch.get_id()} X: {touch.get_x()} Y: {touch.get_y()}")

video_path = "data/mt_camera_raw.mp4"
cap = cv2.VideoCapture(video_path)
if cap.isOpened():
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("HELLO")
server = TuioServer()
current = []
previous = []
send = []
idCounter = 0
current_frame = 0
ms_start, ms_end, ms_time = 0, 0, 0
counter = 0
condition = True
data_ready = False
ret, frame = cap.read()
if not ret:
    condition = False
    print("TERMINATION: Camerastream stopped or last frame of video reached.")
original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# Before the main loop
touch_points_queue = Queue()
demo_process = Process(target=tuiodemo_simulation_matplotlib, args=(touch_points_queue,))
demo_process.start()
# cv2.imshow("background", original)
previous.clear()
current.clear()

while condition:
    ret, frame = cap.read()
    ms_start = time.time()
    current.clear()
    current_frame += 1
    if not ret:
        print("TERMINATION: Camerastream stopped or last frame of video reached.")
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("original video", frame)

    contours, hierarchy = filters(frame, idCounter, current, previous)
    if hierarchy is not None and len(hierarchy) > 0:
        hierarchy = hierarchy[0]
        for idx in range(len(hierarchy)):
            if cv2.contourArea(contours[idx]) > 30 and len(contours[idx]) > 4:
                # fits ellipse around contour
                ellipse = cv2.fitEllipse(contours[idx])
                # draws detected contour ellipse
                cv2.ellipse(frame, ellipse, (200, 200, 200), 1, 8)
                # extracts x and y coordinates from ellipse
                ellipseX, ellipseY = ellipse[0][0], ellipse[0][1]
                # touch initialisation
                new_touch = Touch(ellipseX, ellipseY, current_frame)
                nearest_touch = new_touch.nearest(previous)
                if nearest_touch.get_id() > 0:
                    new_touch.set_id(nearest_touch.get_id())
                else:
                    idCounter += 1
                    new_touch.set_id(idCounter)
                current.append(new_touch)
    #CURRENT EXISTS
    currentcopy=current.copy()
    #TODO add everything here
    print("PREVIOUS:", len(previous))
    print("CURRENT:", len(current))
    #todo strategy 1: new touches in current in previous
    items_to_remove = set()

    for touch1 in current:
        for touch2 in previous:
            if touch1.get_id() == touch2.get_id():
                server=fingerMoved(touch1.get_id(), touch1.get_x(), touch1.get_y(), server)
                items_to_remove.add(touch1)

    # Remove items from currentcopy after iterating
    for item in items_to_remove:
        if item in currentcopy:
            currentcopy.remove(item)

    # todo strategy 2: touches in previous not in current
    for touch1 in previous:
        if touch1 not in currentcopy:
            server=fingerUp(touch1.get_id(),server)

    # todo strategy 3:new touches in current not in previous

    to_add = []
    for touch1 in current:
        if touch1 not in previous:
            to_add.append(touch1)

    for touch1 in to_add:
        server=fingerDown(touch1.get_id(),touch1.get_x(),touch1.get_y(),server)

    print("cursor length for frame ", current_frame, " : ", len(server.cursors))

    '''print("server 1", len(server.cursors))
    # Update the position of existing touch points on the TUIO server
    update_existing_touch_points(previous, current, server)
    print("server 2", len(server.cursors))
    # Add new touch points to the TUIO server
    add_new_touch_points(previous, current, server)
    print("server 3", len(server.cursors))
    # Remove inactive touch points from the TUIO server
    remove_inactive_touch_points(previous, current, server)
    print("server 4", len(server.cursors))'''

    #server.send_bundle()

    if current_frame>49:
        server.send_bundle()
        screen=visualise_touch_events(current,server)
        #cv2.imshow("DEMO", screen)
        print_touch_events(current,server)
        #normalized_touch_points = [(normalize(t.get_x(), t.get_y())) for t in current]
        # data_ready = True
        #touch_points_queue.put(normalized_touch_points)
        #plt=tuiodemo_simulation_matplotlib(touch_points_queue)


    server.cursors.clear()
    #Inside the main loop (after processing the frame and updating the TUIO server)
    #normalized_touch_points = [(normalize(t.get_x(), t.get_y())) for t in current]
    #data_ready = True
    #touch_points_queue.put(normalized_touch_points)

    #TODO till here
    ms_end = time.time()
    ms_time = ms_end - ms_start
    show(current, frame, current_frame, ms_time, previous, server)

    previous = current.copy()  # END
    if cv2.waitKey(30) & 0xFF == ord('q'):
        print("TERMINATION - q")
        break

if condition:
    print("the number of unique touches: ", idCounter)
    print("SUCCESS: Program terminated like expected.")
cap.release()
# After the main loop (to stop the TUIODemo simulation)
touch_points_queue.put("STOP")
demo_process.join()
cv2.destroyAllWindows()
