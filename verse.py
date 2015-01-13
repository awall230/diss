__author__ = 'adamwaller'

import emphases
import numpy as np
import matplotlib.pyplot as plt

class Verse(object):
    """
    Holds various statistics for a given verse as attribute (calculated by emphases.py)
    """

    def __init__(self, filename, name, artist, year):
        self.name = name
        self.artist = artist
        self.filename = "/Users/adamwaller/Documents/Eastman/Dissertation/transcriptions/" + filename
        self.year = year
        self.aggregate_emphases = emphases.get_data(self.filename)

        onset_counters = {}
        emph_counters = {}
        non_emph_counters = {}
        total_weights = 0
        counter = 0
        total_emph_weights = 0
        emph_counter = 0
        total_non_emph_weights = 0
        non_emph_counter = 0
        for holder in self.aggregate_emphases:
            for beat, emph, weight in holder:
                if beat not in onset_counters:
                    onset_counters[beat] = 1
                else:
                    onset_counters[beat] += 1

                if emph > 0:
                    total_emph_weights += weight
                    emph_counter += 1
                    if beat not in emph_counters:
                        emph_counters[beat] = 1
                    else:
                        emph_counters[beat] += 1
                elif emph == 0:
                    total_non_emph_weights += weight
                    non_emph_counter += 1
                    if beat not in non_emph_counters:
                        non_emph_counters[beat] = 1
                    else:
                        non_emph_counters[beat] += 1

                total_weights += weight
                counter += 1

        self.total_onsets = counter
        self.amw = total_weights/counter
        self.stressed_amw = total_emph_weights/emph_counter
        self.unstressed_amw = total_non_emph_weights/non_emph_counter

        self.raw_profile = emphases.get_raw_profile(onset_counters)
        self.profile = emphases.get_profile(self.raw_profile)
        self.entropy = emphases.cross_entropy(self.profile, self.profile)

        self.onset_counters = onset_counters
        self.amw_ratio = self.stressed_amw/self.unstressed_amw
        self.measure_amws = emphases.measure_amws(self.aggregate_emphases)


#Create master list of verses with years for plotting
verses = []
verses.append(Verse("if_i_ruled_the_world.xml", "If I Ruled the World", "Kurtis Blow", 1985))
verses.append(Verse("lets_talk_about_sex.xml", "Let's Talk About Sex", "Salt N Pepa", 1990))
verses.append(Verse("lifes_a_bitch.xml", "Life's a Bitch", "Nas", 1994))
verses.append(Verse("lose_yourself.xml", "Lose Yourself", "Eminem", 2002))

#get metrical profiles
mp = verses[0].raw_profile
for i in range(1, len(verses)):
    mp[:,1] += verses[i].raw_profile[:,1]
mp[:,1] *= 1.0/sum(mp[:,1])
print mp


#---plotting procedures for various statistics---

# plt.plot(verses[3].measure_amws[:,0], verses[3].measure_amws[:,1], 'o-')
# plt.xticks(range(18))
# plt.xlabel("Measure")
# plt.ylabel("Average Metrical Weight (AMW)")
# plt.show()



#plt.plot(verses[3].profile[:,0], verses[3].profile[:,1], 'o-')
#plt.show()

# for v in verses:

# plt.plot(mp[:,0], mp[:,1], 'o-')
# plt.show()

#plt.plot([v.year for v in verses], [v.amw_ratio for v in verses], 'o--')
# plt.plot([v.year for v in verses], [v.stressed_amw for v in verses], 'o-')
# plt.plot([v.year for v in verses], [v.unstressed_amw for v in verses], 'o-')
#plt.show()

# labels = ['Kurtis Blow\n(1985)', 'Salt-N-Pepa\n(1990)', 'Nas\n(1994)', 'Eminem\n(2002)']
# x = [v.year for v in verses]
# plt.plot(x, [v.amw_ratio for v in verses], 'o-')
# plt.xticks(x, labels)
# plt.xlabel('Year')
# plt.ylabel('Stressed AMW / Unstressed AMW')
# plt.show()

# labels = ['Kurtis Blow\n(1985)', 'Salt-N-Pepa\n(1990)', 'Nas\n(1994)', 'Eminem\n(2002)']
# x = [v.year for v in verses]
# plt.plot(x, [v.stressed_amw for v in verses], 'o--', label = "Stressed AMW")
# plt.plot(x, [v.unstressed_amw for v in verses], 'o:', label = "Unstressed AMW")
# plt.legend()
# plt.xticks(x, labels)
# plt.xlabel('Year')
# plt.ylabel('Average Metrical Weight (AMW)')
# plt.show()


#print [v.entropy for v in verses]

# plt.plot([v.year for v in verses], [v.amw for v in verses], 'o-')
# plt.show()