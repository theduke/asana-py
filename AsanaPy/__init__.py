import urllib, urllib2
from urllib2 import URLError

import base64
import json

class AsanaPy:
    
    apiUrl = 'https://app.asana.com/api/1.0/'
    apiKey = None
    
    def __init__(self, apiKey):
        self.apiKey = apiKey
        
    def getUsers(self):
        return self.doRequest('users')
    
    def getUser(self, id, getRaw=False):
        data = self.doRequest('users/' + id)
        return data
        
    def getWorkspaces(self):
        return self.doRequest('workspaces')
    
    # projects
    
    def getProjects(self, workspaceId=None):
        path = 'projects'
        
        if workspaceId: path = 'workspaces/' + workspaceId + '/projects'
        
        return self.doRequest(path)
    
    def updateProject(self, data, id=None):
        if id == None and isinstance(data, Project): id = data.id
        if not id: raise Exception('No id supplied')
        
        return self.doRequest('projects/' + id, data)
    
    # TASKS
    
    def getTasksByWorkspace(self, workspaceId, assigneeId):
        
        path = 'tasks?workspace=' + workspaceId + '&assignee=' + assigneeId
        return self.doRequest(path)
    
    def getTasksByProject(self, projectId):
        
        path = 'tasks?project=' + projectId
        return self.doRequest(path)
    
    def getTask(self, id, getRaw=False):
        data = self.doRequest('tasks/' + id)
        
        return data if getRaw else Task(data)
    
    def createTask(self, data):
        return self.doRequest('tasks', data)
    
    def updateTask(self, data, id=None):
        if id == None and isinstance(data, Task): 
            id = data.id
            data.id = None
            
        if not id: raise Exception('No id supplied')
        
        path = 'tasks/630244425202' # 'tasks/' + id
        
        return self.doRequest(path, data)
    
    def doRequest(self, path, data=None):
        request = urllib2.Request(self.apiUrl + path)
        
        # add auth header
        authHeader = base64.encodestring('%s:%s' % (self.apiKey, ''))[:-1]
        request.add_header("Authorization", "Basic %s" % authHeader)
        
        # add data
        if data:
            if isinstance(data, AsanaObject): data = data.toData() 
            request.add_data(urllib.urlencode(data))
        
        try:
            response = urllib2.urlopen(request)
        except URLError, e:
            data = json.loads(e.read())
            msg = data['errors'][0]['message']
            
            raise Exception('Request "' + path + '" failed: ' + msg)
            
        output = response.read()
        
        responseData = json.loads(output)
        
        return responseData['data']
    
class AsanaObject:
    
    def toData(self):
        data = self.__dict__
        for (key, value) in data.items():
            if value == None: del data[key]
            
        return data
    
    def fromData(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    
class Task(AsanaObject):
    
    def __init__(self, data=None):
        
        self.id = None
        self.assignee = None
        
        # options: inbox, later, today, upcoming
        self.assignee_status = None
        
        # options: true, false
        self.completed = None
        
        # 2012-03-26
        self.due_on = None
        
        self.name = None
        self.notes = None
        self.workspace = None
        
        # read only
        self.created_at = None
        self.completed_at = None
        self.modified_at = None
        self.followers = None
        self.projects = None
        
        if data: self.fromData(data)

class Project(AsanaObject):
    
    def __init__(self, data=None):
        
        self.id = None
        
        # options: true, false
        self.archived = None
        
        self.name = None
        self.notes = None
        self.workspace = None
        
        # read only
        self.created_at = None
        self.modified_at = None
        self.followers = None
        
        if data: self.fromData(data)

if __name__ == '__main__':
    key = '1AOUZjO.xCinSxWsxr8H8YPGkZjJNqbK'
    ap = AsanaPy(key)
    
    wsThedukeId = '71898440933'
    projectSelfImprovementId = '368400820134'
    
    dukeUser = '71880211371'
    taskId = '1076062531085'
    
    t = Task()
    data = {
        'id': '1076062531085',
        'name': 'Test2',
        'notes': 'MyNotes',
        'workspace': wsThedukeId,
        'assignee': 'me',
        'assignee_status': 'inbox'
    }
    t.fromData(data)
    
    p = Project()
    p.id = projectSelfImprovementId
    p.notes = 'blabla'
    
    #ws = ap.getTask('1076062531085', False)
    #ws = ap.getTasksByWorkspace(wsThedukeId, 'me')
    #ws = ap.updateTask({'name': 'Aufraeumen...!'}, '630244425202')
    
    ws = ap.updateProject(p)
    
    print(ws.toData() if isinstance(ws, AsanaObject) else ws)

    