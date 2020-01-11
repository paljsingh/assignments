#!/usr/bin/env python3

import copy
import re


class PatientRecord:
    """ Stores patient info. """

    def __init__(self, age, name, Pid):
        self.PatId = str(Pid) + str(age).rjust(2, '0')
        self.name = name
        self.age = age
        self.left = None
        self.right = None

    def __str__(self):
        """ debugging aid """
        return "{}, {}, {}".format(self.name, self.age, self.PatId)


def next_patient_banner(p):
    """ Generate 'Next Patient' message.

        Return info about the next patient.
    """

    if p is None:
        return ""

    return """---- next patient ---------------
Next patient for consultation is: {}, {}
----------------------------------------------
""".format(p.PatId, p.name)


def _swap(n1, n2):
    """ Swap two nodes. """

    # It is easier to swap the values than all the links.
    n1.age, n2.age = n2.age, n1.age
    n1.name, n2.name = n2.name, n1.name
    n1.PatId, n2.PatId = n2.PatId, n1.PatId


def _max(node1, node2):
    """ Return the node having higher age value,
        or None if both nodes do not exist.
    """

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


def read_in2():
    """ Read the second input file, line by line. """

    infile = 'inputPS5b.txt'
    with open(infile, "r") as f:
        for line in f:
            yield line
    return


def write_out2(file):
    """ Write/append to second output file. """

    outfile = 'outputPS5.txt'
    with open(outfile, "a+") as f:
        f.write(file)
    return


class ConsultQueue:
    """ Build the Consult Queue as a max heap tree.
        For every new patient, the patient id is generated and
        it's record inserted to heap tree and the tree is heapified.
    """

    initial_pid = pid = 1000  # patient counter (initial value.)
    register = dict()  # provide easy mapping b/w patId and patient node.
    queue = list()  # stores the max heap tree
    queue2 = list()  # duplicate list, preserves the original heap for reconstruction.
    root = None  # heap tree's root

    def registerPatient(self, name, age):
        """ Register a patient node.
            - generate a patient ID
            - add the patient node to a max heap tree.

            Return newly added patient node.
        """

        patid = self._generate_pat_id()
        patient = PatientRecord(age, name, patid)
        self.register[patid] = patient
        return self.enqueuePatient(patid)

    def enqueuePatient(self, PatId):
        """ Add patient node to max heap.

            Return patient node.
        """

        patient = self.register[PatId]
        return self._heap_add(patient)

    def nextPatient(self):
        """ Remove next patient from the heap.

            Return deleted patient node (or None).
        """

        if self.root is not None:
            # dequeue root and heapify the tree again.
            return self._dequeuePatient()
        else:
            return None

    def _dequeuePatient(self):
        """ Remove next patient from the heap.
            Argument: patId (unused, as we do not remove arbitrary patient node
            but always the one from the heap's root.)
            Argument kept only for compatibility with the question format.

            Return deleted patient node.
        """
        return self._heap_remove()

    def new_patient_banner(self, p):
        """ Generate 'New Patient' message.
            Return info about the new patient.
        """

        return """---- new patient entered ---------------
Patient details: {}, {}, {}
Refreshed queue:
{}
----------------------------------------------
""".format(p.name, p.age, p.PatId, self._heap_items().rstrip())

    def _generate_pat_id(self):
        """ Generate patient id in <xxxx> form.

            Return Patient Id.
        """

        self.pid += 1
        # patId is like xxxx (eg. 0001)
        patid = str(self.pid).rjust(4, '0')
        return patid

    def _heap_add(self, node):
        """ Add a node to max heap tree and heapify the tree. """

        self.queue.append(node)
        # if heap is empty, add root node and return.
        if self.root is None:
            self.root = node
            return node

        # if heap is not-empty, find the (expected) parent of the new node.
        parent = self.queue[len(self.queue) // 2 - 1]

        # connect the new node to parent's left/right, whichever available.
        if parent.left is None:
            parent.left = node
        else:
            parent.right = node

        # starting from this node, heapify upwards.
        return self._heapify_bottom_up(node)

    def _heap_remove(self):
        """ Remove the root node from max heap tree and heapify the tree.

            Return the deleted (root) node.
        """

        # if there are no more elements to delete
        if len(self.queue) == 0:
            return None

        # else, swap root with last node, heapify, and then pop/return last node.

        # before swapping, remove parent->last_node pointer.
        last_node = self.queue[-1]
        parent = self.queue[len(self.queue) // 2 - 1]
        if parent.left is last_node:
            parent.left = None
        else:
            parent.right = None

        _swap(self.root, last_node)
        root = self.queue.pop(-1)

        # Tree can be empty here.
        if len(self.queue) == 0:
            self.root = None
        else:
            self._heapify_top_down()

        return root

    def _heapify_bottom_up(self, node):
        """ Helper function to heapify the tree from bottom to top.

            Return the original node.
        """

        parent_pos = len(self.queue) // 2 - 1
        parent = self.queue[parent_pos]

        while parent is not None and parent.age < node.age:
            _swap(parent, node)
            node = parent  # move up and compare again

            # calculate current node's parent's index, special handling for root.
            parent_pos = parent_pos // 2 - 1
            if parent_pos < 0:
                parent_pos = 0
            parent = self.queue[parent_pos]

        return node

    def _heapify_top_down(self):
        """ Helper function to heapify the tree from top to bottom.

            Return the (new) root node.
        """

        if self.root is None:
            return

        node = self.root
        while node is not None:
            child = _max(node.left, node.right)
            # if current node's age value is smaller than one of it's child,
            # swap with larger child.
            if child is not None and node.age < child.age:
                _swap(node, child)
                node = child
            else:
                break
        return self.root

    def _heap_items(self):
        """ List heap items in sorted order without changing the heap.
            - Deep copy the original list.
            - Print the max heap as sorted list by removing elements one by one.
            - Restore max heap from the copied list.

            Return string containing patients info sorted by age.
        """

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

    def read_in1(self):
        """ Read initial input file and register the patients. """

        infile = 'inputPS5a.txt'
        with open(infile, "r") as f:
            for line in f:
                # handle 0 or more spaces before/after comma.
                if re.match('^.*,', line):
                    (name, age) = re.split(r' *, *', line.rstrip())
                    age = int(age)
                    self.registerPatient(name, age)
        return

    def write_out1(self):
        """ Write the output generated after initial patients are registered. """

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


def main():
    # create the initial queue from infile1
    cq = ConsultQueue()
    cq.read_in1()

    # write output to outfile1
    cq.write_out1()

    # enqueue new patients from infile2.
    for line in read_in2():
        # we expect either a 'New patient' with name/age info
        # or the 'Next Patient' command
        if re.match('^newPatient:', line):
            # handle 0 or more spaces before/after comma.
            (_, name_age) = re.split(r'newPatient: *', line.rstrip())
            (name, age) = re.split(r', *', name_age.rstrip())
            age = int(age)

            patient = cq.registerPatient(name, age)
            write_out2(cq.new_patient_banner(patient))
        elif re.match('^nextPatient', line):
            patient = cq.nextPatient()
            write_out2(next_patient_banner(patient))


main()
