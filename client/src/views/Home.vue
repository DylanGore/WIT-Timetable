<template>
    <div class="home container-fluid">
        <div class="row">
            <div class="col-sm-12">
                <h1>Timetable Options</h1>
                <form @submit.prevent="get_timetable">
                    <div class="mb-3">
                        <label for="inputDepatment" class="form-label">Department</label>
                        <select id="inputDepatment" v-model="form.department" class="form-select" aria-label="Department select" @change="get_courses($event)">
                            <option v-for="dept in timetableData" :key="dept.code" :value="dept.code">
                                {{ dept.name }}
                            </option>
                        </select>
                        <!-- <div id="departmentHelp" class="form-text">
                            Please input the department identefier from the official timetable (e.g. Computing and Maths is SP, Science is SC, etc.)
                        </div> -->
                    </div>
                    <div v-if="form.department != null" class="mb-3">
                        <label for="inputProgramme" class="form-label">Programme</label>
                        <select id="inputProgramme" v-model="form.programme" class="form-select" aria-label="Programme select">
                            <option v-for="prog in selectedDept.courses" :key="prog.code" :value="prog.code">
                                {{ prog.name }}
                            </option>
                        </select>
                        <!-- <div id="programmeHelp" class="form-text">Please input the programme code from the official timetable (in brackets after the Programme name)</div> -->
                    </div>

                    <div class="btn-toolbar mb-3" role="toolbar" aria-label="Toolbar with button groups">
                        <div class="btn-group mr-2" role="group" aria-label="First group">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="!loading">Get Timetable</span>
                                <span v-else>
                                    <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                                    Loading...
                                </span>
                            </button>
                        </div>
                    </div>
                </form>
                <div v-if="timetable.length > 0" class="col-sm-12">
                    <h3>Display Options</h3>
                    <form v-if="timetable.length > 0">
                        <div class="form-check form-switch mb-3">
                            <input id="switchIgnored" v-model="showIgnored" class="form-check-input" type="checkbox" />
                            <label class="form-check-label" for="switchIgnored">Show ignored events</label>
                        </div>
                        <div class="mb-3">
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-primary" @click="merge_following()" :disabled="eventsMerged">Merge long classes into a single event</button>
                                <button type="button" class="btn btn-primary" @click="remove_prog_code()" :disabled="progCodeRemoved">Remove programme code from name</button>
                            </div>
                        </div>
                    </form>
                </div>
                <div v-if="timetable.length > 0" class="col-sm-12">
                    <h3>Export Options</h3>
                    <form>
                        <div class="mb-3">
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-success" @click="generate_ical()">Download .ical</button>
                            </div>
                        </div>
                    </form>
                </div>
                <hr />
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <section v-if="timetable.length > 0" id="timetable-tabs">
                    <div id="nav-tabContent" class="tab-content">
                        <nav>
                            <div id="nav-tab" class="nav nav-tabs" role="tablist">
                                <a
                                    v-for="day in days"
                                    :id="`nav-${day}-tab`"
                                    :key="day"
                                    :class="tab_classes(day)"
                                    data-bs-toggle="tab"
                                    :href="`#nav-${day}`"
                                    role="tab"
                                    :aria-controls="`nav-${day}`"
                                    aria-selected="true"
                                >
                                    {{ day.charAt(0).toUpperCase() + day.slice(1) }}
                                </a>
                            </div>
                        </nav>

                        <div v-for="day in days" :id="`nav-${day}`" :key="day" :class="content_classes(day)" role="tabpanel" :aria-labelledby="`nav-${day}-tab`">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th scope="col">Start Time</th>
                                        <th scope="col">End Time</th>
                                        <th scope="col">Duration</th>
                                        <th scope="col">Name</th>
                                        <th scope="col">Groups</th>
                                        <th scope="col">Type</th>
                                        <th scope="col">Lecturer</th>
                                        <th scope="col">Room</th>
                                        <th scope="col">Options</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="event in day_classes(day)"
                                        :key="event.id"
                                        :class="{
                                            'oncampus-lecture': event.type.includes('L - On Campus'),
                                            'online-lecture': event.type.includes('OL - Online'),
                                            'online-practical': event.type.includes('OP - Online'),
                                            'oncampus-practical': event.type.includes('P - On Campus'),
                                            'oncampus-tutorial': event.type.includes('T - On Campus'),
                                            'online-tutorial': event.type.includes('OT - Online'),
                                            'online-s': event.type.includes('OS - Online'),
                                            'ignore-class': event.ignore && !showIgnored,
                                            'ignore-class-visible': event.ignore && showIgnored
                                        }"
                                    >
                                        <td>{{ event.time }}</td>
                                        <td>{{ (parseInt(event.time.split(':')[0], 10) + parseInt(event.duration, 10)).toString() + `:${event.time.split(':')[1]}` }}</td>
                                        <td>{{ event.duration }} hrs</td>
                                        <td>{{ event.name }}</td>
                                        <td>
                                            <ul>
                                                <li v-for="group in event.groups" :key="group">
                                                    {{ group }}
                                                </li>
                                            </ul>
                                        </td>
                                        <td class="type-col">
                                            {{ event.type }}
                                        </td>
                                        <td>{{ event.lecturer }}</td>
                                        <td>{{ event.room }}</td>
                                        <td>
                                            <div class="btn-group" role="group">
                                                <!-- prettier-ignore -->
                                                <button id="btnGroupHideEvent" type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
                                                    Hide
                                                </button>
                                                <ul class="dropdown-menu" aria-labelledby="btnGroupHideEvent">
                                                    <li><a class="dropdown-item" @click="ignore_event(event.id)">Hide event</a></li>
                                                    <li><a class="dropdown-item" @click="ignore_event_group(event.id)">Hide all events with matching groups</a></li>
                                                    <li><a class="dropdown-item" @click="ignore_event_name(event.id)">Hide all events with this name</a></li>
                                                </ul>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import timetable_data from '../json/timetable.json';
import ical from 'ical-generator';
import slugify from 'slugify';
import { addDays, addHours, parse } from 'date-fns';

export default {
    name: 'Home',
    data() {
        return {
            form: {
                department: null,
                programme: null
            },
            optionsForm: {
                removeProgrammeCode: true,
                calendarType: 'microsoft'
            },
            selectedDept: null,
            loading: false,
            timetableData: timetable_data,
            days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            activeDay: 'monday',
            timetable: [],
            ical: null,
            allGroups: [],
            availableGroups: [],
            showIgnored: false,
            eventsMerged: false,
            progCodeRemoved: false
        };
    },
    computed: {},
    methods: {
        get_timetable: function () {
            this.loading = true;
            this.timetable = [];
            axios.post('/get-timetable', this.$data.form).then((res) => {
                this.loading = false;
                this.progCodeRemoved = false;
                this.eventsMerged = false;
                this.timetable = res.data.timetable;
                this.timetable.forEach((entry) => {
                    this.allGroups = [...new Set([...this.allGroups, ...entry.groups])];
                    this.availableGroups = this.allGroups;
                });
            });
        },
        merge_following: function () {
            var mergedTimetable = this.timetable;
            mergedTimetable.forEach((entry, index, arr) => {
                var nextTime = (parseInt(entry.time.split(':')[0], 10) + 1).toString() + `:${entry.time.split(':')[1]}`;
                // console.log(nextTime);
                var similarEvents = arr.filter((event) => event.time == nextTime && event.day == entry.day);

                similarEvents.forEach((simEvent) => {
                    // console.log('similar event: ', simEvent);
                    if (entry.name == simEvent.name && this.compareGroups(simEvent.groups, entry.groups) && entry.type == simEvent.type && entry.room == simEvent.room) {
                        // console.log('match');
                        entry.duration = (parseInt(simEvent.duration, 10) + 1).toString();
                        mergedTimetable.splice(
                            mergedTimetable.findIndex((x) => x.id === simEvent.id),
                            1
                        );
                    }
                });
            });
            this.eventsMerged = true;
        },
        remove_prog_code: function () {
            this.timetable.forEach((event) => {
                var newNameArr = event.name.split(' ');
                newNameArr.shift(); // Remove the first entry (programme code)
                event.name = newNameArr.join(' '); // Join the remaining array into a single string
            });
            this.progCodeRemoved = true;
        },
        get_courses: function (event) {
            this.selectedDept = this.timetableData.filter((item) => item.code == event.target.value)[0];
            return this.timetableData.filter((item) => item.code == event.target.value);
        },
        day_classes: function (day) {
            return this.timetable.filter((event) => event.day === day.charAt(0).toUpperCase() + day.slice(1));
        },
        tab_classes: function (day) {
            if (this.activeDay === day) {
                return 'nav-link active';
            } else {
                return 'nav-link';
            }
        },
        content_classes: function (day) {
            if (this.activeDay === day) {
                return 'tab-pane fade table-responsive show active';
            } else {
                return 'tab-pane fade table-responsive';
            }
        },
        generate_ical: function () {
            var curr = new Date('Jan 25 2021 00:00:00');
            // curr.setHours(0, 0, 0, 0);
            var first = curr.getDate() - curr.getDay(); // First day is the day of the month - the day of the week
            var firstday = addDays(new Date(curr.setDate(first)), 1);

            const calendar = ical({
                domain: 'wit-timetable.dylangore.ie',
                prodId: { company: 'Dylan Gore', product: 'wit-timetable' },
                name: 'WIT Timetable',
                timezone: 'Europe/Dublin'
            });

            this.timetable.forEach((entry) => {
                if (!entry.ignore) {
                    let start = parse(entry.time, 'HH:mm', addDays(firstday, this.days.indexOf(entry.day.toLowerCase())));
                    let location = entry.room;
                    if (entry.online) {
                        location = location.concat(' (Online)');
                    }
                    console.log(start);
                    let calEvent = calendar.createEvent({
                        uid: slugify(`${entry.name}-${entry.time}-${entry.day}`),
                        start: start,
                        end: addHours(start, entry.duration),
                        summary: entry.name,
                        description: `Lecturer: ${entry.lecturer} \nType: ${entry.type}\nLocation: ${location}`,
                        busystatus: 'busy',
                        location: location
                    });

                    var excludedDays = [];

                    // Exclude Easter
                    var timeOffStart = new Date('Mar 29 2021 00:00:00');
                    var timeOffEnd = new Date('Apr 9 2021 23:59:59');

                    var currDate = timeOffStart;
                    while (currDate < timeOffEnd) {
                        currDate.setHours(start.getHours() + 1);
                        currDate.setMinutes(start.getMinutes());
                        excludedDays.push(currDate);
                        currDate = addDays(currDate, 1);
                    }

                    // Exclude St. Patrick's Day
                    currDate = new Date('Mar 17 2021 00:00:00');
                    currDate.setHours(start.getHours());
                    currDate.setMinutes(start.getMinutes());
                    excludedDays.push(currDate);

                    // Create repeat rule
                    calEvent.repeating({
                        freq: 'WEEKLY',
                        until: new Date('May 1 2021 00:00:00'),
                        byDay: [entry.day.toLowerCase().substring(0, 2)],
                        exclude: excludedDays
                    });
                }
            });

            // console.log(calendar.toString());
            // this.ical = calendar.toString();

            this.download_file('wit.ics', calendar.toString().replaceAll('0Z', '0'));
            // this.download_file('wit.ics', calendar.toString());
        },
        ignore_event: function (id, ignore = true) {
            let event = this.timetable.find((x) => x.id === id);
            let eventIdx = this.timetable.findIndex((x) => x.id === id);

            event.ignore = ignore;

            this.timetable[eventIdx] = event;
        },
        ignore_event_group: function (id, ignore = true) {
            let event = this.timetable.find((x) => x.id === id);

            this.timetable.forEach((foundEvent) => {
                if (this.arrayEquals(foundEvent.groups, event.groups)) {
                    foundEvent.ignore = ignore;
                    console.log('Ignoring: ' + event.time + event.name);
                }
            });
        },
        ignore_event_name: function (id, ignore = true) {
            let event = this.timetable.find((x) => x.id === id);

            this.timetable.forEach((foundEvent) => {
                if (foundEvent.name == event.name) {
                    foundEvent.ignore = ignore;
                    console.log('Ignoring: ' + event.time + event.name);
                }
            });
        },
        download_file: function (filename, text) {
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);
        },
        // https://masteringjs.io/tutorials/fundamentals/compare-arrays
        arrayEquals: function (a, b) {
            console.log('comparing arrays');
            return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((val, index) => val === b[index]);
        },
        compareGroups: function (arr1, arr2) {
            var match = false;
            if (arr1.length == arr2.length) {
                arr1.forEach((group, idx) => {
                    if (group == arr2[idx]) {
                        match = true;
                    } else {
                        match = false;
                    }
                });
            }
            return match;
        }
    }
};
</script>

<style lang="css">
.ignore-class {
    display: none;
}

.ignore-class-visible {
    text-decoration: line-through;
}

.oncampus-lecture {
    background: aqua;
}
.online-lecture {
    background: aqua;
}

.online-s {
    background: green;
}

.online-s > .type-col {
    background: #71c7ec;
}

.online-lecture > .type-col {
    background: #71c7ec;
}
.oncampus-practical {
    background: orange;
}
.online-practical {
    background: orange;
}

.online-practical > .type-col {
    background: #ff4d00;
}

.oncampus-tutorial {
    background: #ff80c0;
}
.online-tutorial {
    background: #ff80c0;
}
.online-tutorial > .type-col {
    background: #ff0055;
}
</style>
