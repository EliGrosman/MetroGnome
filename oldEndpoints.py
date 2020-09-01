
@app.route('/generateLocations', methods = ['POST'])
def generateLocations():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400

  file = request.files['audioFile']

  if file and allowed_file(file.filename):

    converted, sr, newName = convert_file(file, file.filename, file.filename + "_converted.wav_", app.config['CONVERT_FOLDER'])
    _, beats = generate_beats(converted, sr)

    ret = {
      "beats": beats.tolist(),
      "sr": sr,
    }

    response = make_response(send_file(os.path.join(app.config['CONVERT_FOLDER'], newName), attachment_filename = "converted.wav", as_attachment = True))
    response.headers['X-Beats'] = ret

    return response, 200

  else:
    return render_template('badFileType.html'), 400


@app.route('/generateTrack', methods = ['POST'])
def generateTrack():
  if 'audioFile' not in request.files:
    return render_template("noAudioFile.html"), 400

  click_freq = request.args.get("click_freq")
  click_dur = request.args.get("click_dur")

  if click_freq is None or click_dur is None:
    return render_template('badFileType.html'), 400

  file = request.files['audioFile']
  
  if file and allowed_file(file.filename):

    letters = string.ascii_lowercase
    hashName = ''.join(random.choice(letters) for i in range(16))

    converted, sr, newName = convert_file(file, file.filename, hashName + "_converted.wav", app.config['CONVERT_FOLDER'])
    retName = generate_click_only(converted, file.filename, hashName + "_clicks.wav", float(click_freq), float(click_dur), app.config['CLICKS_FOLDER'])

    response = make_response()
    response.headers['X-Urls'] = { "key": hashName }

    return response, 200

  else: 

    return render_template('badFileType.html'), 400

@app.route('/get/<filename>')
def converted_file(filename):
  if '_' in filename:

    ext = filename.rsplit('_', 1)[1].lower()

    if(ext == "converted.wav"):
      return send_from_directory(app.config['CONVERT_FOLDER'], filename)
    elif(ext == "clicks.wav"):
      return send_from_directory(app.config['CLICKS_FOLDER'], filename)
    else:
      return render_tempalte("error.html"), 400
  else:
    return render_tempalte("error.html"), 400