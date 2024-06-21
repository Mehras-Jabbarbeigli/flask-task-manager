$(document).ready(function() {
    $('#external-events .fc-event').each(function() {
        let eventTitle = $.trim($(this).text());
        $(this).data('event', {
            title: eventTitle,
            stick: true
        });

        $(this).draggable({
            zIndex: 999,
            revert: true,
            revertDuration: 0
        });
    });

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        editable: true,
        droppable: true,
        events: '/fetch_tasks',
        drop: handleDropEvent,
        eventDrop: handleEventDrop,
        eventResize: handleEventResize
    });

    $('#taskForm').on('submit', function(event) {
        event.preventDefault();

        let title = $('#taskTitle').val();
        let description = $('#taskDescription').val();

        createNewTask(title, description);
    });

    function handleDropEvent(date, jsEvent, ui) {
        let taskId = $(this).data('task-id');
        let newDate = date.format();

        updateTaskPosition(taskId, newDate, newDate);

        if (!$(this).data('dropped')) {
            $(this).data('dropped', true);
            location.reload();
        }
    }

    function handleEventDrop(event, delta, revertFunc) {
        let start = event.start.format();
        let end = (event.end ? event.end.format() : start);

        updateTaskPosition(event.id, start, end, revertFunc);
    }

    function handleEventResize(event, delta, revertFunc) {
        let start = event.start.format();
        let end = event.end.format();

        updateTaskPosition(event.id, start, end, revertFunc);
    }

    function createNewTask(title, description) {
        let taskType = $('#taskType').val();

        $.ajax({
            type: 'POST',
            url: '/add_task',
            data: {
                title: title,
                desc: description,
                taskType: taskType,
                csrf_token: '{{ csrf_token() }}'
            },
            success: function(response) {
                addTaskToList(response.sno, title);
                clearFormFields();
                closeModal();
                reloadPage();
                addTaskToCalendar(title);
            },
            error: function(xhr, status, error) {
                console.error('Error creating task:', error);
            }
        });
    }

    function updateTaskPosition(taskId, startDate, endDate, revertFunc = null) {
        $.ajax({
            type: 'POST',
            url: '/update_task_position',
            data: {
                taskId: taskId,
                startDate: startDate,
                endDate: endDate
            },
            success: function(response) {
                console.log('Task position updated successfully.');
            },
            error: function(xhr, status, error) {
                console.error('Error updating task position:', error);
                if (revertFunc) revertFunc();
            }
        });
    }

    function addTaskToList(taskId, title) {
        let newTask = $('<div class="fc-event" data-task-id="' + taskId + '">' + title + '</div>');
        $('#task-list').append(newTask);

        newTask.data('event', {
            title: $.trim(newTask.text()),
            stick: true
        }).draggable({
            zIndex: 999,
            revert: true,
            revertDuration: 0
        });
    }

    function clearFormFields() {
        $('#taskTitle').val('');
        $('#taskDescription').val('');
    }

    function closeModal() {
        $('#createTaskModal').modal('hide');
    }

    function reloadPage() {
        location.reload();
    }

    function addTaskToCalendar(title) {
        $('#calendar').fullCalendar('renderEvent', {
            title: title,
            start: new Date(),
            allDay: true
        }, true);
    }
});
