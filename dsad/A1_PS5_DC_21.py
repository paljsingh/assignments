#!/usr/bin/env python3

import re
import copy

class PatientRecord:

    def __init__(self, age, name, Pid):
        self.PatId = str(Pid) + str(age).rjust(2,'0')
        self.name = name
        self.age = age
        self.left = None
        self.right = None

    def __str__(self):
        return "{}, {}, {}".format(self.name, self.age, self.PatId)

# Build the Consult Queue as a max heap tree.
#
# For every new patient, the patient id is generated and
# it's record inserted to heap tree and the tree is sorted.
class ConsultQueue:

    initial_pid = pid = 1000  # patient counter (initial value ?)
    register = dict()   # dict to provide easy mapping b/w patId and patient node.
    queue = list()      # stores the max heap tree
    queue2 = list()     # duplicate list, to preserve the original heap/queue for reconstruction.
    root = None         # heap tree's root

    """
        nothing to see here.
    """
    def __init__(self):
        pass


    """
        registerPatient:
            Register a patient node.
            - generates a patient ID
            - adds the patient node to a max heap tree.
        
        Returns:
            Newly added patient node.
    """
    def registerPatient(self, name, age):
        patid = self._generate_pat_id(name, age)
        patient = PatientRecord(age, name, patid)
        self.register[patid] = patient
        return self.enqueuePatient(patid)


    """
        enqueuePatient:
            Add patient node to max heap.

        Returns:
            Patient node.
    """
    def enqueuePatient(self, PatId):
        patient = self.register[PatId]
        return self._heap_add(patient)


    """
        nextPatient:
            Print next patient info.
            Remove next patient from the heap.

        Returns:
            Deleted patient node.
    """
    def nextPatient(self):
        if self.root is not None:
            self.write_out2(self.next_patient_banner(self.root))
            return self._dequeuePatient(self.root.PatId)  # dequeue root and sort the heap again.
        else:
            return None


    """
        _dequeuePatient:
            Remove next patient from the heap.

        Returns:
            Deleted patient node.
    """
    def _dequeuePatient(self, patid=None):
        return self._heap_remove()  # always going to remove from the top.


    """
        new_patient_banner:
            Return info about the new patient.
    """
    def new_patient_banner(self, p):
        return """---- new patient entered ---------------
Patient details: {}, {}, {}
Refreshed queue:
{}
----------------------------------------------
""".format(p.name, p.age, p.PatId, self._heap_items().rstrip())


    """
        next_patient_banner:
            Return info about the next patient.
    """
    def next_patient_banner(self, p):
        if p is None:
            return ""

        return """---- next patient ---------------
Next patient for consultation is: {}, {}
----------------------------------------------
""".format(p.PatId, p.name)


    """
        _generate_pat_id:
            Return Patient Id in <xxxx> form.
    """
    def _generate_pat_id(self, age, name):
        self.pid += 1
        # patId is like xxxx (eg. 0001)
        patid = str(self.pid).rjust(4, '0')
        return patid


    """
        _swap:
            Swap two given nodes.
    """
    def _swap(self, n1, n2):
        # It is easier to swap the values than all the links.
        n1.age, n2.age = n2.age, n1.age
        n1.name, n2.name = n2.name, n1.name
        n1.PatId, n2.PatId = n2.PatId, n1.PatId

    """
        _max:
            Return the node having higher age value,
            or None if both nodes do not exist.
    """
    def _max(self, node1, node2):
        if node1 is None and node2 is None:
            return None

        if node1 is None:
            return node2
        if node2 is None:
            return node1

        if node1.age > node2.age:
            return node1
        else:
            return node2

    """
        _heap_add:
            Add a node to max heap tree,
            and sort/heapify the tree.
    """
    def _heap_add(self, node):
        self.queue.append(node)
        # if heap is empty, add root node and return.
        if self.root is None:
            self.root = node
            return node

        # for every other node, find it's immediate parent.
        parent = self.queue[len(self.queue) // 2 -1]

        # connect the new node to parent's left/right, whichever available.
        if parent.left is None:
            parent.left = node
        else:
            parent.right = node

        # starting from this node, sort upwards.
        return self._heapify_bottom_up(node)

    """
        _heap_remove:
            Remove the root node from max heap tree,
            and sort/heapify the tree.
    """
    def _heap_remove(self):
        # if there are no more elements to dequeue
        if len(self.queue) == 0:
            return None

        # swap root with last node, heapify, and then pop/return last node.
        last_node = self.queue[-1]

        if len(self.queue) > 1:
            parent = self.queue[len(self.queue)//2 -1]
            if parent.left is last_node:
                parent.left = None
            else:
                parent.right = None
            self._swap(self.root, last_node)

        root = self.queue.pop(-1)
        self._heapify_top_down()

        return root

    """
        _heapify_bottom_up:
            Helper function to heapify the tree from bottom to top.
    """
    def _heapify_bottom_up(self, node):
        parent = self.queue[len(self.queue) // 2 -1]

        while parent is not None and parent.age < node.age:
            self._swap(parent, node)
            node = parent      # move up and compare again
        return node

    """
        _heapify_top_down:
            Helper function to heapify the tree from top to bottom.
    """
    def _heapify_top_down(self):
        node = self.root
        while node is not None:
            child = self._max(node.left, node.right)
            # if current node's age value is smaller than one of it's child,
            # swap with larger child.
            if child is not None and node.age < child.age:
                self._swap(node, child)
                node = child
            else:
                break
        return self.root

    """
        _heap_items
            Deep copy the original list.
            Print the max heap as sorted list by removing elements one by one.
            Restore max heap from the copied list.
        Returns
            String output containing patient info sorted by age.
    """
    def _heap_items(self):
        # deep-copy the original list/heap for later restoration
        self.queue2 = copy.deepcopy(self.queue)

        output = ""
        while len(self.queue) > 0:
            node = self._dequeuePatient()
            output += "{}, {}\n".format(node.PatId, node.name)

        # restore original list/heap
        self.queue = self.queue2
        self.root = self.queue[0]

        return output

    """
        heap_items_via_queue_sort:
            Make a copy of the original queue,
            uses python's built-in list.sort() method
            to sort the copy.
            Return heap items in sorted manner.

        This is not used,  _heap_items is called instead.
    """
    def _heap_items_via_queue_sort(self):
        q = self.queue.copy()
        q.sort(key=lambda a: a.age, reverse=True)
        output = ""
        for p in q:
            output += "{}, {}\n".format(p.PatId, p.name)

        return output

    """
        read_in1:
            Read initial input file and register the patients.
    """
    def read_in1(self):
        infile = 'inputPS5a.txt'
        with open(infile, "r") as f:
            for line in f:
                # handle 0 or more spaces before/after comma.
                if re.match('^.*,', line):
                    (name, age) = re.split(r' *, *', line.rstrip())
                    age = int(age)
                    self.registerPatient(name, age)
        return

    """
        write_out1:
            Write the output generated after initial patients are registered.
    """
    def write_out1(self):
        outfile = 'outputPS5.txt'
        with open(outfile, "w") as f:
            text = """---- initial queue ---------------
No of patients added: {}
Refreshed queue:
{}
----------------------------------------------
""".format(self.pid - self.initial_pid, self._heap_items().rstrip())
            f.write(text)
        return

    """
        read_in2:
            Read the second input file, line by line
    """
    def read_in2(self):
        infile = 'inputPS5b.txt'
        with open(infile, "r") as f:
            for line in f:
                yield line
        return

    """
        write_out2:
            Write/append to second output file
    """
    def write_out2(self, str):
        outfile = 'outputPS5.txt'
        with open(outfile, "a+") as f:
            f.write(str)
        return


def main():

    # create the initial queue from infile1
    cq = ConsultQueue()
    cq.read_in1()

    # write output to outfile1
    cq.write_out1()

    # enqueue new patients from infile2.
    for line in cq.read_in2():
        # we expect either a 'New patient' with name/age info
        # or the 'Next Patient' command
        if re.match('^newPatient:', line):
            # handle 0 or more spaces before/after comma.
            (_, name_age) = re.split(r'newPatient: *', line.rstrip())
            (name, age) = re.split(r', *', name_age.rstrip())
            age = int(age)
            patient = cq.registerPatient(name, age)
            cq.write_out2(cq.new_patient_banner(patient))
        elif re.match('^nextPatient', line):
            cq.nextPatient()


main()