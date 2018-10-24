from jack import readers
from jack.core import QASetting

fastqa_reader = readers.reader_from_file("../fastqa_reader")

# support = """"It is a replica of the grotto at Lourdes, France where the Virgin Mary reputedly appeared to Saint Bernadette Soubirous in 1858. At the end of the main drive (and in a direct line that connects through 3 statues and the Gold Dome), is a simple, modern stone statue of Mary."""

support = ''
with open('testdata.txt') as myfile: 
	support = myfile.read()

#question = "Whom does he do?"
#question = "To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?"
question = "Where is gibraltar?"
answers = fastqa_reader([QASetting(
    question= question,
    support=[support]
)])
print("\n\n")
print("The Context is = " + support + "\n\n") 
print("The question is = " + question+ "\n\n")
print(answers[0][0].text +  "\n\n")