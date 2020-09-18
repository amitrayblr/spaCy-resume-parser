import spacy
import pandas as pd
import re
import os

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler

nlp = spacy.load('en_core_web_md')
ner = spacy.load('custom-ner')

matcher = Matcher(nlp.vocab)

ruler = EntityRuler(nlp).from_disk("./patterns.jsonl")
nlp.add_pipe(ruler)

def textExtract(filename, pages=None):
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

def nameExtract(text):
  for ent in nlp(text).ents:
    if(ent.label_ == 'PERSON'):
      return ent.text
    else:
      pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
      matcher.add('NAME', [pattern])
      matches = matcher(nlp(text))
      for match_id, start, end in matches:
        span = nlp(text)[start:end]
        return span.text

def numberExtract(text):
  phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{5})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
  if phone:
    number = ''.join(phone[0])
    if len(number) > 10:
      return '+' + number
    else:
      return number

def linkExtract(text):
  urls = []
  links = re.findall(r'(https?://\S+)', text)
  for ele in links:
    if ele not in urls:
      urls.append(ele)
  email = re.findall(r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', text)
  if email:
    try:
      urls.append(email[0].split()[0].strip(';'))
    except IndexError:
      urls.append('Could not extract email')
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
    text = textExtract(os.path.join(dir, entry))
    text = " ".join(text.split())
    clean = re.sub('[^A-Za-z0-9 ]+', '', text)

    print('Name is:', nameExtract(clean))
    print('Numbers found', numberExtract(text))
    print('Links found:', linkExtract(text))
    print('Qualifications found:', qualificationExtract(clean))
    # print('Education is:', educationExtract(text))
    print('Skills found:', skillsExtract(clean))
    print('-----------------------------------------------')

parseResume('resumes')
