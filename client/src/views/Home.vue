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
                    <!-- <div class="mb-3">
                        <label for="inputProgramme" class="form-label">Programme Code</label>
                        <input id="inputDepartment" v-model="form.programme" type="text" class="form-control" name="programme" required />
                        <div id="programmeHelp" class="form-text">Please input the programme code from the official timetable (in brackets after the Programme name)</div>
                    </div> -->

                    <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
                        <div class="btn-group mr-2" role="group" aria-label="First group">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="!loading">Get Timetable</span>
                                <span v-else>
                                    <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                                    Loading...
                                </span>
                            </button>
                        </div>

                        <div class="btn-group" role="group" aria-label="Third group">
                            <button v-if="timetable.length > 0" class="btn btn-info" role="button" @click="generate_ical()">Generate ICS</button>
                        </div>
                    </div>
                </form>
                <form v-if="timetable.length > 0">
                    <div class="row">
                        <div class="col-sm-6">
                            <label for="inputAddAvailableGroup" class="form-label">Available groups</label>
                            <select id="inputAddAvailableGroup" v-model="groupForm.availableAdd" class="form-select" size="4" aria-label="Available groups">
                                <option v-for="group in availableGroups" :key="group" :value="group">
                                    {{ group }}
                                </option>
                            </select>
                            <br />
                            <button class="btn btn-info btn-sm" role="button" @click.prevent="add_wanted_group()">Add Selected Group</button>
                        </div>
                        <div class="col-sm-6">
                            <label for="inputAddGroup" class="form-label">Wanted groups</label>
                            <select id="inputAddGroup" v-model="groupForm.availableRemove" class="form-select" size="4" aria-label="Wanted groups">
                                <option v-for="group in groupFilters.add" :key="group" :value="group">
                                    {{ group }}
                                </option>
                            </select>
                            <br />
                            <button class="btn btn-danger btn-sm" role="button" @click.prevent="remove_wanted_group()">Remove Selected Group</button>
                        </div>
                    </div>
                    <!-- <div class="mb-3">
                        <label for="inputRemoveGroup" class="form-label">Unwanted groups</label>
                        <select id="inputRemoveGroup" v-model="groupForm.remove" class="form-select" aria-label="Unwanted groups">
                            <option v-for="group in availableGroups" :key="group" :value="group">
                                {{ group }}
                            </option>
                        </select>
                        <br />
                        <button class="btn btn-info" role="button" @click="add_unwanted_group()">Add Group</button>
                    </div> -->
                </form>
                <hr />
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <section v-if="timetable.length > 0" id="timetable-tabs">
                    <nav>
                        <div id="nav-tab" class="nav nav-tabs" role="tablist">
                            <a
                                v-for="day in days"
                                :id="`nav-${day}-tab`"
                                :key="day"
                                :class="tab_classes(day)"
                                data-toggle="tab"
                                :href="`#nav-${day}`"
                                role="tab"
                                :aria-controls="`nav-${day}`"
                                aria-selected="true"
                            >
                                {{ day.charAt(0).toUpperCase() + day.slice(1) }}
                            </a>
                        </div>
                    </nav>
                    <div id="nav-tabContent" class="tab-content">
                        <div v-for="day in days" :id="`nav-${day}`" :key="day" :class="content_classes(day)" role="tabpanel" :aria-labelledby="`nav-${day}-tab`">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th scope="col">Time</th>
                                        <th scope="col">Name</th>
                                        <th scope="col">Groups</th>
                                        <th scope="col">Type</th>
                                        <th scope="col">Lecturer</th>
                                        <th scope="col">Room</th>
                                        <th scope="col">Ignored</th>
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
                                            'ignore-class': event.ignore
                                        }"
                                    >
                                        <td>{{ event.time }}</td>
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
                                        <td>{{ event.ignore }}</td>
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
import { addDays, addHours, parse } from 'date-fns';

export default {
    name: 'Home',
    data() {
        return {
            form: {
                department: null,
                programme: null
            },
            groupForm: {
                availableAdd: [],
                availableRemove: []
            },
            groupFilters: {
                add: [],
                remove: []
            },
            selectedDept: null,
            loading: false,
            timetableData: timetable_data,
            days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            activeDay: 'monday',
            timetable: [],
            ical: null,
            allGroups: [],
            enabledGroups: null,
            availableGroups: []
            // toRemove: [],
        };
    },
    computed: {
        filteredTimetable: function () {
            this.timetable.forEach((entry) => {
                if (this.groupFilters.add.some((v) => entry.groups.indexOf(v) !== -1)) {
                    if (entry.id > -1) {
                        console.log(`Ignoring ${entry.time} ${entry.name}`);
                        entry.ignore = true;
                    } else {
                        console.log(`Un-Ignoring ${entry.time} ${entry.name}`);
                        entry.ignore = false;
                    }
                }
                // if (this.groupFilters.remove.some((v) => entry.groups.indexOf(v) === -1)) {
                //     if (entry.id > -1) {
                //         entry.ignore = true;
                //     }
                // }
            });
            return this.timetable;
        }
    },
    methods: {
        get_timetable: function () {
            this.loading = true;
            this.timetable = [];
            axios.post('http://10.0.1.1:5000/get-timetable', this.$data.form).then((res) => {
                this.loading = false;
                this.timetable = res.data.timetable;
                this.timetable.forEach((entry) => {
                    this.allGroups = [...new Set([...this.allGroups, ...entry.groups])];
                    this.availableGroups = this.allGroups;
                });
            });
        },
        get_courses: function (event) {
            this.selectedDept = this.timetableData.filter((item) => item.code == event.target.value)[0];
            return this.timetableData.filter((item) => item.code == event.target.value);
        },
        day_classes: function (day) {
            return this.filteredTimetable.filter((event) => event.day === day.charAt(0).toUpperCase() + day.slice(1));
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
        add_wanted_group: function () {
            this.groupFilters.add.push(this.groupForm.availableAdd);
            this.availableGroups = this.availableGroups.filter((e) => e !== this.groupForm.availableAdd);
        },
        remove_wanted_group: function () {
            this.timetable.forEach((entry) => {
                entry.ignore = false;
            });
            this.availableGroups = this.allGroups;
            this.groupFilters.add = [];
        },
        add_unwanted_group: function () {
            this.groupFilters.remove.push(this.groupForm.remove);
            this.availableGroups = this.availableGroups.filter((e) => e !== this.groupForm.remove);
        },
        generate_ical: function () {
            var curr = new Date('Sept 28 2020 00:00:00 UTC'); // get current date
            // curr.setHours(0, 0, 0, 0);
            var first = curr.getDate() - curr.getDay(); // First day is the day of the month - the day of the week

            var firstday = addDays(new Date(curr.setDate(first)), 1);

            const calendar = ical({
                domain: 'wit-timetable.apps.dylangore.space',
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
                        start: start,
                        end: addHours(start, 1),
                        summary: entry.name,
                        description: `Lecturer: ${entry.lecturer} \nType: ${entry.type}`,
                        location: location,
                        busystatus: 'busy'
                    });

                    calEvent.repeating({
                        freq: 'WEEKLY',
                        until: new Date('Dec 19 2020 00:00:00 UTC')
                    });
                }
            });

            // console.log(calendar.toString());
            // this.ical = calendar.toString();

            this.download_file('wit.ics', calendar.toString());
        },
        download_file: function (filename, text) {
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);
        }
    }
};
</script>

<style lang="css">
.ignore-class {
    text-decoration: line-through;
    display: none;
}

.oncampus-lecture {
    background: aqua;
}
.online-lecture {
    background: aqua;
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
