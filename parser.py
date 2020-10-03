import spacy
import pandas as pd
import re
import os
import json
import textract

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage

from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler

nlp = spacy.load('en_core_web_md')
ner = spacy.load('custom-ner')

matcher = Matcher(nlp.vocab)

ruler = EntityRuler(nlp).from_disk("./patterns.jsonl")
nlp.add_pipe(ruler)

def pdfExtract(filename, pages=None):
  if not pages:
      pagenumber = set()
  else:
      pagenumber = set(pages)

  output = StringIO()
  manager = PDFResourceManager()
  converter = TextConverter(manager, output, laparams=LAParams())
  interpreter = PDFPageInterpreter(manager, converter)

  file = open(filename, 'rb')
  for page in PDFPage.get_pages(file, pagenumber):
      interpreter.process_page(page)
  file.close()
  converter.close()
  text = output.getvalue()
  output.close
  return text

def docExtract(filename):
  text = textract.process(filename)
  text = str(text, 'utf-8')
  return text

def nameExtract(text):  
  pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
  matcher.add('NAME', [pattern])
  matches = matcher(text)
  # print(matches)
  for match_id, start, end in matches:
    span = text[start:end]
    if 'name' not in span.text.lower():
      # print(span.text)
      return span.text

def numberExtract(text):
  phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2,3})\s*(?:[.-]\s*)?([0-9]{4,5})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
  if phone:
    number = ''.join(phone[0])
    if len(number) > 10:
      return '+' + number
    else:
      return number

def emailExtract(text):
  email = re.findall(r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', text)
  if email:
    return email
  else: 
    return None

def linkExtract(text):
  urls = []
  links = re.findall(r'(https?://\S+)', text)
  for ele in links:
    if ele not in urls:
      urls.append(ele)
  if (len(urls) != 0):
    return urls
  else:
    return ('Could not extract any links')

def skillsExtract(text, skills_file='skills.csv'):
  tokens = [token.text for token in nlp(text)]
  data = pd.read_csv(skills_file)
  skills = list(data.columns.values)
  skillset = []

  for token in tokens:
    if token.lower() in skills:
      skillset.append(token)

  for chunk in nlp(text).noun_chunks:
    chunk = chunk.text.lower().strip()
    if chunk in skills:
      skillset.append(chunk)

  return [i.capitalize() for i in set([i.lower() for i in skillset])]

def educationExtract(text):
  education = []
  for ent in ner(text).ents:
    if (ent.label_ == 'UNIVERSITY'):
      education.append(ent.text)
    if (ent.label_ == 'SCHOOL'):
      education.append(ent.text)

  return education

def qualificationExtract(text):
  qualifications = []
  low = text.lower()
  for ent in nlp(low).ents:
    if (ent.label_ == 'DEGREE'):
      qualifications.append(ent.text)
  for ent in nlp(text).ents:
    if (ent.label_ == 'DEGREE'):
      qualifications.append(ent.text)    
  if (len(qualifications) > 0):
    return qualifications
  else: 
    return ('Could not extract qualifications')  

def parseResume(dir):
  entries = os.listdir(dir)
  for entry in entries:
    ext = os.path.splitext(entry)[-1].lower()
    if (ext == '.pdf'):
      text = pdfExtract(os.path.join(dir, entry))
      text = " ".join(text.split())
      clean = re.sub('[^A-Za-z0-9 ]+', '', text)
    else:
      text = docExtract(os.path.join(dir, entry))
      text = " ".join(text.split())
      clean = re.sub('[^A-Za-z0-9 ]+', '', text)

    name = nameExtract(nlp(text))
    number = numberExtract(text)
    email = emailExtract(text)
    # links = linkExtract(text)
    # quali = qualificationExtract(clean)
    skill = skillsExtract(clean)

    # print('Name is:', nameExtract(clean))
    # print('Numbers found', numberExtract(text))
    # print('Links found:', linkExtract(text))
    # print('Qualifications found:', qualificationExtract(clean))
    # # print('Education is:', educationExtract(text))
    # print('Skills found:', skillsExtract(clean))

    resumeDict = {
      'basics': {
      },
      'skills': []
    }

    if (name != None):
      resumeDict['basics']['name'] = name
    else:
      resumeDict['basics']['name'] = None

    if (number != None):
      resumeDict['basics']['mobile'] = number
    else:
      resumeDict['basics']['mobile'] = None

    if (email != None):
      resumeDict['basics']['email'] = email
    else:
      resumeDict['basics']['email'] = None

    # if (len(skill) > 0):
    #   for i in skill:
    #     resumeDict['skills'].append({'name': i})
    print(name)
    # print(json.dumps(resumeDict, indent=2))
    print('-----------------------------------------------')

parseResume('docx')
