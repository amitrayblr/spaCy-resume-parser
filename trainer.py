import spacy
import random

TRAIN_DATA = [
  ('i study at national public school', {'entities': [(11, 33, 'SCHOOL')]}),
  ('chirst university is where im studying', {'entities': [(0, 17, 'UNIVERSITY')]}),
  ('i am going to pes university', {'entities': [(14, 28, 'UNIVERSITY')]}),
  ('i graduated from indian institue of iechnology madras', {'entities': [(17, 53, 'UNIVERSITY')]}),
  ('bmc university is where i work', {'entities': [(0, 14, 'UNIVERSITY')]}),
  ('i am going to grduate from op jindal university', {'entities': [(27, 47, 'UNIVERSITY')]}),
  ('the international school bangalore is my school', {'entities': [(0, 34, 'SCHOOL')]}),
  ('greenwood high international is where i studied', {'entities': [(0, 28, 'SCHOOL')]}),
  ('i want to go to ashoka university', {'entities': [(16, 33, 'UNIVERSITY')]}),
  ('i want to study at flame university', {'entities': [(19, 35, 'UNIVERSITY')]}),
  ('stanford university is an ivy league university', {'entities': [(0, 19, 'UNIVERSITY')]}),
  ('university of massachussets is the best university for engineering', {'entities': [(0, 27, 'UNIVERSITY')]}),
  ('university of oslo is a good university', {'entities': [(0, 18, 'UNIVERSITY')]}),
  ('i want to study at university of british colombia', {'entities': [(19, 49, 'UNIVERSITY')]}),
  ('delhi public school is a terrible school', {'entities': [(0, 19, 'SCHOOL')]}),
  ('ebenzer international is an international school', {'entities': [(0, 21, 'SCHOOL')]}),
  ('bethany public school is where i started my schooling', {'entities': [(0, 21, 'SCHOOL')]}),
  ('cambride university is a top uk university', {'entities': [(0, 19, 'UNIVERSITY')]}),
]

def trainModel(data, iter):
  TRAIN_DATA = data
  nlp = spacy.blank('en')
  if 'ner' not in nlp.pipe_names:
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

  for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
      ner.add_label(ent[2])

  other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
  with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(iter):
      print("Statring iteration " + str(itn))
      random.shuffle(TRAIN_DATA)
      losses = {}
      for text, annotations in TRAIN_DATA:
        nlp.update([text], [annotations], drop=0.2, sgd=optimizer, losses=losses)
      print(losses)
  return nlp

model = trainModel(TRAIN_DATA, 20)
model.to_disk('custom-ner')
