<template>
    <div class="home container-fluid">
        <div class="row">
            <div class="col-sm-12">
                <h1>Timetable Options</h1>
                <form @submit.prevent="get_timetable">
                    <!-- <div class="mb-3">
                        <label for="inputDepartment" class="form-label">Department</label>
                        <input type="text" class="form-control" id="inputDepartment" name="department" v-model="form.department" required />
                        <div id="departmentHelp" class="form-text">Please input the department identefier from the official timetable (e.g. Computing and Maths is SP, Science is SC, etc.)</div>
                    </div> -->
                    <div class="mb-3">
                        <label for="inputDepatment" class="form-label">Department</label>
                        <select class="form-select" id="inputDepatment" aria-label="Department select" v-model="form.department" @change="get_courses($event)">
                            <option v-for="dept in timetableData" :key="dept.code" :value="dept.code">{{ dept.name }}</option>
                        </select>
                    </div>
                    <div class="mb-3" v-if="form.department != null">
                        <label for="inputProgramme" class="form-label">Programme</label>
                        <select class="form-select" id="inputProgramme" aria-label="Programme select" v-model="form.programme">
                            <option v-for="prog in selectedDept.courses" :key="prog.code" :value="prog.code">{{ prog.name }}</option>
                        </select>
                        <!-- <div id="programmeHelp" class="form-text">Please input the programme code from the official timetable (in brackets after the Programme name)</div> -->
                    </div>
                    <!-- <div class="mb-3">
                        <label for="inputProgramme" class="form-label">Programme Code</label>
                        <input type="text" class="form-control" id="inputDepartment" name="programme" v-model="form.programme" required />
                        <div id="programmeHelp" class="form-text">Please input the programme code from the official timetable (in brackets after the Programme name)</div>
                    </div> -->

                    <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
                        <div class="btn-group mr-2" role="group" aria-label="First group">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="!loading">Get Timetable</span>
                                <span v-else><span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span> Loading...</span>
                            </button>
                        </div>

                        <div class="btn-group" role="group" aria-label="Third group">
                            <button class="btn btn-info" role="button" @click="generate_ical()" v-if="timetable.length > 0">Generate ICS</button>
                        </div>
                    </div>
                </form>
                <hr />
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <section id="timetable-tabs" v-if="timetable.length > 0">
                    <nav>
                        <div class="nav nav-tabs" id="nav-tab" role="tablist">
                            <a :class="tab_classes(day)" :id="`nav-${day}-tab`" data-toggle="tab" :href="`#nav-${day}`" role="tab" :aria-controls="`nav-${day}`" aria-selected="true" v-for="day in days" :key="day">{{ day.charAt(0).toUpperCase() + day.slice(1) }}</a>
                        </div>
                    </nav>
                    <div class="tab-content" id="nav-tabContent">
                        <div :class="content_classes(day)" :id="`nav-${day}`" role="tabpanel" :aria-labelledby="`nav-${day}-tab`" v-for="day in days" :key="day">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th scope="col">Time</th>
                                        <th scope="col">Name</th>
                                        <th scope="col">Groups</th>
                                        <th scope="col">Type</th>
                                        <th scope="col">Lecturer</th>
                                        <th scope="col">Room</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="event in day_classes(day)"
                                        :key="event.id"
                                        :class="{
                                            'oncampus-lecture': event.type.includes('L - OnCampus'),
                                            'online-lecture': event.type.includes('OL - OnLine'),
                                            'online-practical': event.type.includes('OP - OnLine'),
                                            'oncampus-practical': event.type.includes('P - OnCampus'),
                                            'oncampus-tutorial': event.type.includes('T - OnCampus'),
                                            'online-tutorial': event.type.includes('OT - OnLine'),
                                        }"
                                    >
                                        <td>{{ event.time }}</td>
                                        <td>{{ event.name }}</td>
                                        <td>
                                            <ul>
                                                <li v-for="group in event.groups" :key="group">{{ group }}</li>
                                            </ul>
                                        </td>
                                        <td class="type-col">{{ event.type }}</td>
                                        <td>{{ event.lecturer }}</td>
                                        <td>{{ event.room }}</td>
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
                programme: null,
            },
            // groupForm: {
            //     wanted: [],
            //     ignored: [],
            // },
            selectedDept: null,
            loading: false,
            timetableData: timetable_data,
            days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            activeDay: 'monday',
            timetable: [],
            ical: null,
            groups: [],
            // toRemove: [],
        };
    },
    computed: {},
    methods: {
        get_timetable: function() {
            this.loading = true;
            this.timetable = [];
            axios.post('http://10.0.1.1:5000/get-timetable', this.$data.form).then((res) => {
                this.loading = false;
                this.timetable = res.data.timetable;

                let groups = [];
                this.timetable.forEach((entry) => {
                    groups = [...new Set([...groups, ...entry.groups])];
                });
                this.groups = groups;
            });
        },
        // update_groups: function() {
        //     this.timetable.forEach((entry) => {
        //         // Remove ignored
        //         if (this.groupForm.ignored.some((v) => entry.groups.indexOf(v) !== -1)) {
        //             if (entry.id > -1) {
        //                 // this.toRemove.push(entry.id);
        //                 entry.ignore = true;
        //             }
        //         }
        //         // Remove unwanted
        //         if (this.groupForm.wanted.some((v) => entry.groups.indexOf(v) === -1)) {
        //             if (entry.id > -1) {
        //                 entry.ignore = true;
        //                 // this.toRemove.push(entry.id);
        //             }
        //         }
        //     });
        // },
        get_courses: function(event) {
            this.selectedDept = this.timetableData.filter((item) => item.code == event.target.value)[0];
            return this.timetableData.filter((item) => item.code == event.target.value);
        },
        day_classes: function(day) {
            return this.timetable.filter((event) => event.day === day.charAt(0).toUpperCase() + day.slice(1));
        },
        tab_classes: function(day) {
            if (this.activeDay === day) {
                return 'nav-link active';
            } else {
                return 'nav-link';
            }
        },
        content_classes: function(day) {
            if (this.activeDay === day) {
                return 'tab-pane fade table-responsive show active';
            } else {
                return 'tab-pane fade table-responsive';
            }
        },
        generate_ical: function() {
            var curr = new Date('Sept 28 2020 00:00:00 UTC'); // get current date
            // curr.setHours(0, 0, 0, 0);
            var first = curr.getDate() - curr.getDay(); // First day is the day of the month - the day of the week

            var firstday = addDays(new Date(curr.setDate(first)), 1);

            const calendar = ical({
                domain: 'wit-timetable.apps.dylangore.space',
                prodId: { company: 'Dylan Gore', product: 'wit-timetable' },
                name: 'WIT Timetable',
                timezone: 'Europe/Dublin',
            });

            this.timetable.forEach((entry) => {
                let start = parse(entry.time, 'HH:mm', addDays(firstday, this.days.indexOf(entry.day.toLowerCase())));
                console.log(start);
                let calEvent = calendar.createEvent({
                    start: start,
                    end: addHours(start, 1),
                    summary: entry.name,
                    description: `Lecturer: ${entry.lecturer} \nType: ${entry.type}`,
                    location: entry.room,
                    busystatus: 'busy',
                });

                calEvent.repeating({
                    freq: 'WEEKLY',
                    until: new Date('Dec 19 2020 00:00:00 UTC'),
                });
            });

            // console.log(calendar.toString());
            // this.ical = calendar.toString();

            this.download_file('wit.ics', calendar.toString());
        },
        download_file: function(filename, text) {
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);
        },
    },
};
</script>

<style lang="css">
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
