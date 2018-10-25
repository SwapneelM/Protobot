from jack import readers
from jack.core import QASetting

fastqa_reader = readers.reader_from_file("./fastqa_reader")

# Test on a file with stored, unformatted data
support = ''
with open('testdata.txt') as myfile:
	support = myfile.read()

#question = "Whom does he do?"
#question = "To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?"
question = "Where is gibraltar?"
answers = fastqa_reader([QASetting(
    question = question,
    support = [support]
)])

print("The question is = " + question + "\n")
print(answers[0][0].text +  "\n")

support = """Donald John Trump (born June 14, 1946) is the 45th and current President of the United States. Before entering politics, he was a businessman and television personality. Trump was born and raised in the New York City borough of Queens. He received an economics degree from the Wharton School of the University of Pennsylvania and was appointed president of his family's real estate business in 1971, renamed it The Trump Organization, and expanded it from Queens and Brooklyn into
Manhattan. The company built or renovated skyscrapers, hotels, casinos, and golf courses. Trump later started various side ventures, including licensing his name for real estate and consumer products. He managed the company until his 2017 inauguration. He co-authored several books, including The Art of the Deal. He owned the Miss Universe and Miss USA beauty pageants from 1996 to 2015, and he produced and hosted the reality television show The Apprentice from 2003 to 2015. 
Forbes estimates his net worth to be $3.1 billion. 
Trump entered the 2016 presidential race as a Republican and defeated sixteen opponents in the primaries. Commentators described his political positions as populist, protectionist, and nationalist. His campaign received extensive free media coverage many of his public statements were controversial or false. Trump was elected president in a surprise victory over Democratic nominee Hillary Clinton. He became the oldest and wealthiest person ever to assume the
presidency, the first without prior military or government service, and the fifth to have won the election while losing the popular vote. 
His election and policies have sparked numerous protests. Many of his comments and actions have been perceived as racially charged or racist. 
During his presidency, Trump ordered a travel ban on citizens from several Muslim-majority countries, citing security concerns after legal challenges, the Supreme Court upheld the policy's third revision. He signed tax
cut legislation which also rescinded the individual insurance mandate provision of the Affordable Care Act and opened the Arctic Refuge for oil drilling. 
He enacted a partial repeal of the Dodd-Frank Act that had imposed stricter constraints on banks in the aftermath of the 2008 financial crisis. He pursued his America First agenda in foreign policy, withdrawing the U.S. from the Trans-Pacific Partnership trade negotiations, the Paris Agreement on climate change, and the Iran nuclear deal. He
recognized Jerusalem as the capital of Israel, and imposed import tariffs on various goods, triggering a trade war with China. After Trump dismissed FBI Director James Comey, the Justice Department appointed Robert Mueller as Special Counsel to investigate any links and/or coordination between the Trump campaign and the Russian government in its election interference. Trump has repeatedly denied accusations of collusion and obstruction of justice, calling the investigation a politically
motivated witch hunt."""

question="Who is Donald Trump?"
answers = fastqa_reader([QASetting(
    question = question,
    support = [support]
)])

print("The question is = " + question + "\n")
print(answers[0][0].text +  "\n")

question="Whom did he fire?"
answers = fastqa_reader([QASetting(
    question = question,
    support = [support]
)])

print("The question is = " + question + "\n")
print(answers[0][0].text +  "\n")


support = """"It is a replica of the grotto at Lourdes,
France where the Virgin Mary reputedly appeared to Saint Bernadette Soubirous in 1858.
At the end of the main drive (and in a direct line that connects through 3 statues and the Gold Dome),
is a simple, modern stone statue of Mary."""

question="To whom did the Virgin Mary allegedly appear in France?"
answers = fastqa_reader([QASetting(
    question = question,
    support = [support]
)])

print("The question is = " + question + "\n")
print(answers[0][0].text +  "\n")
