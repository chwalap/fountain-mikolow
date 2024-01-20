/*
todo:
*/


let selectedItemId = null;
let createNewItemCallback = null;
let selectCallback = null;
let saveCallback = null;
let isNewItemBeingCreated = null;

function selectableList_SetTitle(title) {
  document.getElementById('selectable-list-title').textContent = title;
}

function validIdRange(id) {
  return id != null && (id >= 0 && id < selectable_list_entries.length);
}

function callSelectCallback(itemId) {
  if (typeof selectCallback === 'function') {
    updateSelectableItemStyles(itemId);
    selectCallback(itemId);
  } else {
    createNotification('error', 'No selectCallback set!');
  }
}

function updateSelectableItemStyles(itemId) {
  var selectableItems = document.querySelectorAll('#selectable-list li');
  selectableItems.forEach((item, index) => {
    if (index === itemId) {
      item.classList.add('selected-list-item');
    } else {
      item.classList.remove('selected-list-item');
    }
    item.setAttribute('onclick', `callSelectCallback(${index})`);
  });
}

function callSaveCallback(itemId) {
  if (typeof saveCallback === 'function') {
    saveCallback(itemId);
  } else {
    createNotification('error', 'No saveCallback set!');
  }
}

function showNoEntriesMessage(show) {
  if (show) {
    document.getElementById('no-entries-message').classList.remove('hidden');
  } else {
    document.getElementById('no-entries-message').classList.add('hidden');
  }
}

function newSelectableEntry() {
  if (isNewItemBeingCreated) {
    return;
  }

  if (typeof createNewItemCallback !== 'function') {
    createNotification('error', 'No createNewItemCallback set!');
    return;
  }

  if (isSaveRequired(selectedItemId)) {
    askToSave(selectedItemId);
    return;
  }

  let inputBox = createInputBox();
  let newListItem = inputBox.parentNode;

  showNoEntriesMessage(false);
  isNewItemBeingCreated = true;

  let eventHandler = () => {
    inputBox.removeEventListener('keypress', keypressEventHandler);
    inputBox.removeEventListener('focusout', focusoutEventHandler);
    let newItemName = inputBox.value.trim();

    if (newItemName) {
      if (!selectableItemExists(newItemName)) {
        isNewItemBeingCreated = false;

        selectable_list_entries.push(createNewItemCallback(newItemName));
        selectedItemId = selectable_list_entries.length - 1;

        newListItem.innerHTML = `<div class="selectable-list-item">${newItemName}</div>`;
        newListItem.setAttribute('onclick', `callSelectCallback(${selectedItemId})`);

        callSelectCallback(selectedItemId);
        callSaveCallback(selectedItemId);
      } else {
        createNotification('warning', `${newItemName} już istnieje!`);
        inputBox.focus();
        inputBox.addEventListener('keypress', keypressEventHandler);
        inputBox.addEventListener('focusout', focusoutEventHandler);
      }
    } else {
      createNotification('warning', 'Podaj nazwę.');
      inputBox.focus();
      inputBox.addEventListener('keypress', keypressEventHandler);
      inputBox.addEventListener('focusout', focusoutEventHandler);
    }

    showNoEntriesMessage(selectable_list_entries.length == 0);
  };

  let keypressEventHandler = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      eventHandler();
    }
  };

  let focusoutEventHandler = (e) => {
    eventHandler();
  };

  inputBox.addEventListener('keypress', keypressEventHandler);
  inputBox.addEventListener('focusout', focusoutEventHandler);
}

function selectableItemExists(itemName) {
  return selectable_list_entries.find(e => e.name == itemName);
}

function createInputBox() {
  var selectableList = document.getElementById('selectable-list');
  var newListItem = document.createElement('li');
  var inputBox = document.createElement('input');
  inputBox.type = 'text';
  inputBox.placeholder = 'Wpisz nazwę';
  inputBox.classList.add('new-selectable-item-input');

  newListItem.appendChild(inputBox);
  selectableList.appendChild(newListItem);
  inputBox.focus();
  return inputBox;
}

function isSaveRequired(itemId) {
  return validIdRange(itemId) &&
         selectable_list_entries[itemId].hasOwnProperty('requireSaving') &&
         selectable_list_entries[itemId].requireSaving;
}

function requireSaving(itemId, require) {
  selectable_list_entries[itemId].requireSaving = require;
}

document.addEventListener('DOMContentLoaded', () => {
  if (selectable_list_entries.length > 0) {
    selectedItemId = 0;
    callSelectCallback(selectedItemId);
  }
});
