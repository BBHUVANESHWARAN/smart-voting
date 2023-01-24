import cv2, sys, numpy, os

def face_register(voter_id):
    print(voter_id)
    sub_data = str(voter_id)
    haar_file = "haarcascade_frontalface_alt2.xml"
    datasets = './datasets'  
    size = 4
    print('Recognizing Face Please Be in sufficient Lights...') 
    (images, lables, names, id) = ([], [], {}, 0) 
    for (subdirs, dirs, files) in os.walk(datasets): 
        for subdir in dirs: 
            names[id] = subdir 
            subjectpath = os.path.join(datasets, subdir) 
            for filename in os.listdir(subjectpath): 
                path = subjectpath + '/' + filename 
                lable = id
                images.append(cv2.imread(path, 0)) 
                lables.append(int(lable)) 
            id += 1
    (width, height) = (130, 100) 
    (images, lables) = [numpy.array(lis) for lis in [images, lables]] 
    print(images,lables)
    if len(images) == 0:
        path = os.path.join(datasets, sub_data) 
        if not os.path.isdir(path):
            os.mkdir(path)   
            (width, height) = (130, 100) 
        face_cascade = cv2.CascadeClassifier(haar_file) 
        webcam = cv2.VideoCapture(0)
        su=1
        er=1
        count = 1  
        while count<50:  
            (_, im) = webcam.read() 
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
            faces = face_cascade.detectMultiScale(gray, 1.3, 4) 
            for (x, y, w, h) in faces: 
                cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
                face = gray[y:y + h, x:x + w] 
                face_resize = cv2.resize(face, (width, height)) 
                cv2.imwrite('% s/% s.png' % (path, count), face_resize) 
            count += 1
            cv2.imshow('OpenCV', im) 
            key = cv2.waitKey(10) 
            if key == 27: 
                break
        webcam.release()
        cv2.destroyAllWindows()
        return 'success'
    else:
        model = cv2.face.LBPHFaceRecognizer_create() 
        model.train(images, lables) 
        face_cascade = cv2.CascadeClassifier(haar_file) 
        webcam = cv2.VideoCapture(0)
        su=1
        er=1
        # webcam = cv2.VideoCapture(0)  
        count = 1
        while count<50:  
            (_, im) = webcam.read() 
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
            faces = face_cascade.detectMultiScale(gray, 1.3, 4) 
            for (x, y, w, h) in faces: 
                cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
                face = gray[y:y + h, x:x + w] 
                face_resize = cv2.resize(face, (width, height)) 
                prediction = model.predict(face_resize) 
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3) 
                if prediction[1]<70:
                    cv2.putText(im, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
                    print('prediction')
                    su+=1
                else:
                    cv2.putText(im, 'recognized',  (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
                    print('recognize')
                    er+=1
            count += 1
            cv2.imshow('OpenCV', im) 
            key = cv2.waitKey(10) 
            if key == 27: 
                break
            elif er >=20:
                path = os.path.join(datasets, sub_data) 
                if not os.path.isdir(path):
                    os.mkdir(path)   
                (width, height) = (130, 100)   
                cv2.imwrite('% s/% s.png' % (path, count), face_resize) 
                webcam.release()
                cv2.destroyAllWindows()
                print('success')
                return 'success'
            elif su >= 10:
                print('your are already registered')
                webcam.release()
                cv2.destroyAllWindows()
                print('error')
                return 'already registered'
         
    

